import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
import io
import re


class CovidData:
    """Classe responsável por armazenar e gerenciar os dados de COVID-19"""

    def __init__(self, date: str, municipality: str, new_cases: int = 0, new_deaths: int = 0,
                 new_vaccinated: int = 0, accumulated_cases: int = 0, accumulated_deaths: int = 0,
                 accumulated_vaccinated: int = 0, **kwargs):
        try:
            # Tenta diferentes formatos de data
            self.date = self._parse_date(date)
        except:
            self.date = datetime.now()

        self.municipality = str(municipality)
        self.new_cases = int(new_cases) if str(new_cases).isdigit() else 0
        self.new_deaths = int(new_deaths) if str(new_deaths).isdigit() else 0
        self.new_vaccinated = int(new_vaccinated) if str(new_vaccinated).isdigit() else 0
        self.accumulated_cases = int(accumulated_cases) if str(accumulated_cases).isdigit() else 0
        self.accumulated_deaths = int(accumulated_deaths) if str(accumulated_deaths).isdigit() else 0
        self.accumulated_vaccinated = int(accumulated_vaccinated) if str(accumulated_vaccinated).isdigit() else 0

        # Armazena campos extras
        self.extra_fields = kwargs

    def _parse_date(self, date_str: str) -> datetime:
        """Tenta parsear diferentes formatos de data"""
        date_formats = [
            "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d",
            "%d-%m-%Y", "%m-%d-%Y", "%d.%m.%Y", "%m.%d.%Y",
            "%Y.%m.%d", "%Y%m%d", "%d%m%Y"
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except ValueError:
                continue

        # Se nenhum formato funcionou, tenta extrair números
        numbers = re.findall(r'\d+', str(date_str))
        if len(numbers) >= 3:
            try:
                # Assume formato mais comum baseado no tamanho dos números
                if len(numbers[0]) == 4:  # Ano primeiro
                    return datetime(int(numbers[0]), int(numbers[1]), int(numbers[2]))
                elif len(numbers[2]) == 4:  # Ano último
                    return datetime(int(numbers[2]), int(numbers[1]), int(numbers[0]))
                else:
                    return datetime(2025, int(numbers[1]), int(numbers[0]))
            except ValueError:
                pass

        raise ValueError(f"Formato de data não reconhecido: {date_str}")

    def get_month_year(self) -> str:
        """Retorna mês e ano no formato MM/YYYY"""
        return f"{self.date.month:02d}/{self.date.year}"


class FlexibleCSVProcessor:
    """Processador CSV/TXT flexível com detecção automática de estrutura"""

    @staticmethod
    def detect_delimiter(sample_text: str) -> str:
        """Detecta automaticamente o delimitador do arquivo"""
        if not sample_text:
            return ','

        # Tenta usar o Sniffer do CSV
        try:
            sniffer = csv.Sniffer()
            sample_lines = '\n'.join(sample_text.split('\n')[:10])
            delimiter = sniffer.sniff(sample_lines, delimiters=',;\t|').delimiter
            return delimiter
        except:
            pass

        # Detecção manual baseada na primeira linha
        first_line = sample_text.split('\n')[0] if sample_text else ""

        # Conta ocorrências de diferentes delimitadores
        delimiter_counts = {
            '\t': first_line.count('\t'),
            ';': first_line.count(';'),
            ',': first_line.count(','),
            '|': first_line.count('|')
        }

        # Retorna o delimitador com mais ocorrências
        return max(delimiter_counts.items(), key=lambda x: x[1])[0]

    @staticmethod
    def detect_column_types(headers: List[str], sample_rows: List[List[str]]) -> Dict[str, str]:
        """Detecta automaticamente o tipo de cada coluna baseado em nome e conteúdo"""
        column_mapping = {}

        for i, header in enumerate(headers):
            header_lower = header.lower().strip()
            column_type = FlexibleCSVProcessor._classify_column(header_lower, sample_rows, i)
            if column_type:
                column_mapping[header] = column_type

        return column_mapping

    @staticmethod
    def _classify_column(header: str, sample_rows: List[List[str]], col_index: int) -> Optional[str]:
        """Classifica uma coluna baseada no nome e conteúdo"""

        # Classificação por nome do cabeçalho
        date_patterns = ['data', 'date', 'fecha', 'dia', 'day', 'datum']
        municipality_patterns = ['municipio', 'cidade', 'city', 'municipality', 'localidade', 'local', 'lugar']
        new_cases_patterns = ['novos_casos', 'new_cases', 'casos_novos', 'daily_cases', 'casos_diarios']
        new_deaths_patterns = ['novos_obitos', 'novos_mortes', 'new_deaths', 'obitos_novos', 'mortes_novas',
                               'daily_deaths']
        new_vaccinated_patterns = ['novos_vacinados', 'new_vaccinated', 'vacinados_novos', 'daily_vaccinated']
        acc_cases_patterns = ['casos_acumulados', 'accumulated_cases', 'total_casos', 'cumulative_cases']
        acc_deaths_patterns = ['obitos_acumulados', 'mortes_acumuladas', 'accumulated_deaths', 'total_obitos',
                               'total_mortes']
        acc_vaccinated_patterns = ['vacinados_acumulados', 'accumulated_vaccinated', 'total_vacinados',
                                   'cumulative_vaccinated']

        # Verifica padrões no nome
        for pattern in date_patterns:
            if pattern in header:
                return 'date'

        for pattern in municipality_patterns:
            if pattern in header:
                return 'municipality'

        for pattern in new_cases_patterns:
            if pattern in header:
                return 'new_cases'

        for pattern in new_deaths_patterns:
            if pattern in header:
                return 'new_deaths'

        for pattern in new_vaccinated_patterns:
            if pattern in header:
                return 'new_vaccinated'

        for pattern in acc_cases_patterns:
            if pattern in header:
                return 'accumulated_cases'

        for pattern in acc_deaths_patterns:
            if pattern in header:
                return 'accumulated_deaths'

        for pattern in acc_vaccinated_patterns:
            if pattern in header:
                return 'accumulated_vaccinated'

        # Se não encontrou pelo nome, analisa o conteúdo
        if col_index < len(sample_rows[0]) if sample_rows else False:
            return FlexibleCSVProcessor._analyze_column_content(sample_rows, col_index)

        return None

    @staticmethod
    def _analyze_column_content(sample_rows: List[List[str]], col_index: int) -> Optional[str]:
        """Analisa o conteúdo da coluna para determinar seu tipo"""
        if not sample_rows or col_index >= len(sample_rows[0]):
            return None

        sample_values = []
        for row in sample_rows[:10]:  # Analisa apenas as primeiras 10 linhas
            if col_index < len(row):
                sample_values.append(row[col_index].strip())

        if not sample_values:
            return None

        # Verifica se parece com data
        date_like_count = 0
        for value in sample_values:
            if re.match(r'\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}', value) or \
                    re.match(r'\d{1,2}[-/\.]\d{1,2}[-/\.]\d{4}', value):
                date_like_count += 1

        if date_like_count > len(sample_values) * 0.7:
            return 'date'

        # Verifica se parece com texto (município)
        text_count = 0
        for value in sample_values:
            if not value.isdigit() and value and not re.match(r'^\d+[\.,]?\d*$', value):
                text_count += 1

        if text_count > len(sample_values) * 0.7:
            return 'municipality'

        # Se é numérico, tenta determinar se é novo, acumulado, etc.
        numeric_values = []
        for value in sample_values:
            try:
                numeric_values.append(float(value.replace(',', '.')))
            except:
                pass

        if numeric_values:
            avg_value = sum(numeric_values) / len(numeric_values)
            max_value = max(numeric_values)

            # Heurística simples: valores maiores tendem a ser acumulados
            if avg_value > 100 or max_value > 1000:
                return 'accumulated_cases'  # Assumindo que é casos acumulados
            else:
                return 'new_cases'  # Assumindo que são casos novos

        return None

    @staticmethod
    def parse_flexible_csv(content: str) -> List[Dict]:
        """Processa conteúdo CSV de forma flexível"""
        if not content.strip():
            return []

        delimiter = FlexibleCSVProcessor.detect_delimiter(content)

        try:
            csv_reader = csv.reader(io.StringIO(content), delimiter=delimiter)
            rows = list(csv_reader)
        except Exception as e:
            print(f"Erro ao ler CSV: {e}")
            return []

        if not rows:
            return []

        # Detecta se há cabeçalho
        has_header = FlexibleCSVProcessor._has_header_row(rows[0])

        if has_header:
            headers = [h.strip() for h in rows[0]]
            data_rows = rows[1:]
        else:
            # Gera cabeçalhos genéricos
            headers = [f"coluna_{i + 1}" for i in range(len(rows[0]))]
            data_rows = rows

        if not data_rows:
            return []

        # Detecta tipos de coluna
        column_mapping = FlexibleCSVProcessor.detect_column_types(headers, data_rows[:10])

        # Converte para lista de dicionários
        parsed_data = []
        for row in data_rows:
            if len(row) < 2:  # Pula linhas muito vazias
                continue

            row_dict = {}
            for i, value in enumerate(row):
                if i < len(headers):
                    header = headers[i]
                    row_dict[header] = value.strip() if value else ""

            # Adiciona mapeamento de tipos
            row_dict['_column_mapping'] = column_mapping
            parsed_data.append(row_dict)

        return parsed_data

    @staticmethod
    def _has_header_row(first_row: List[str]) -> bool:
        """Detecta se a primeira linha é um cabeçalho"""
        if not first_row:
            return False

        # Palavras que indicam cabeçalho
        header_indicators = [
            'data', 'municipio', 'casos', 'obitos', 'mortes', 'vacinados',
            'date', 'city', 'cases', 'deaths', 'vaccinated', 'municipality',
            'acumulado', 'accumulated', 'total', 'novo', 'new', 'daily'
        ]

        text_cells = 0
        for cell in first_row:
            cell_lower = cell.lower().strip()
            if any(indicator in cell_lower for indicator in header_indicators):
                return True
            if not cell.replace('.', '').replace(',', '').replace('-', '').replace('/', '').isdigit():
                text_cells += 1

        # Se mais da metade das células não são números, provavelmente é cabeçalho
        return text_cells > len(first_row) / 2


class FlexibleDataProcessor:
    """Processador de dados flexível que trabalha com qualquer estrutura"""

    def __init__(self):
        self.data: List[CovidData] = []
        self.original_columns: List[str] = []
        self.column_mapping: Dict[str, str] = {}

    def load_data_from_text(self, text_data: str) -> bool:
        """Carrega dados a partir de texto de forma flexível"""
        try:
            parsed_data = FlexibleCSVProcessor.parse_flexible_csv(text_data)

            if parsed_data:
                return self._process_flexible_data(parsed_data)
            else:
                return False

        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return False

    def _process_flexible_data(self, parsed_data: List[Dict]) -> bool:
        """Processa dados flexíveis extraindo informações relevantes"""
        if not parsed_data:
            return False

        self.data = []

        # Pega o mapeamento de colunas do primeiro item
        first_item = parsed_data[0]
        column_mapping = first_item.get('_column_mapping', {})

        # Cria mapeamento reverso para encontrar colunas por tipo
        type_to_column = {}
        for column, col_type in column_mapping.items():
            type_to_column[col_type] = column

        self.original_columns = list(first_item.keys())
        self.original_columns = [col for col in self.original_columns if col != '_column_mapping']
        self.column_mapping = column_mapping

        # Processa cada linha
        for row_dict in parsed_data:
            try:
                # Extrai campos principais usando mapeamento
                covid_data = self._extract_covid_data(row_dict, type_to_column)
                if covid_data:
                    self.data.append(covid_data)
            except Exception as e:
                print(f"Erro ao processar linha: {e}")
                continue

        return len(self.data) > 0

    def _extract_covid_data(self, row_dict: Dict, type_to_column: Dict) -> Optional[CovidData]:
        """Extrai dados COVID-19 de uma linha usando mapeamento flexível"""

        # Campos obrigatórios
        date_col = type_to_column.get('date')
        municipality_col = type_to_column.get('municipality')

        # Se não encontrou data e município pelos tipos, tenta pela posição
        if not date_col or not municipality_col:
            columns = [col for col in row_dict.keys() if col != '_column_mapping']
            if len(columns) >= 2:
                date_col = date_col or columns[0]  # Primeira coluna como data
                municipality_col = municipality_col or columns[1]  # Segunda coluna como município

        if not date_col or not municipality_col:
            return None

        date_value = row_dict.get(date_col, '')
        municipality_value = row_dict.get(municipality_col, '')

        if not date_value or not municipality_value:
            return None

        # Campos opcionais
        kwargs = {
            'new_cases': self._safe_get_numeric(row_dict, type_to_column.get('new_cases')),
            'new_deaths': self._safe_get_numeric(row_dict, type_to_column.get('new_deaths')),
            'new_vaccinated': self._safe_get_numeric(row_dict, type_to_column.get('new_vaccinated')),
            'accumulated_cases': self._safe_get_numeric(row_dict, type_to_column.get('accumulated_cases')),
            'accumulated_deaths': self._safe_get_numeric(row_dict, type_to_column.get('accumulated_deaths')),
            'accumulated_vaccinated': self._safe_get_numeric(row_dict, type_to_column.get('accumulated_vaccinated'))
        }

        # Se não encontrou campos específicos, tenta inferir pela posição
        if all(v == 0 for v in kwargs.values()):
            columns = [col for col in row_dict.keys() if col != '_column_mapping']
            if len(columns) >= 3:
                # Assume ordem padrão após data e município
                for i, field in enumerate(['new_cases', 'new_deaths', 'new_vaccinated',
                                           'accumulated_cases', 'accumulated_deaths', 'accumulated_vaccinated']):
                    if i + 2 < len(columns):
                        kwargs[field] = self._safe_get_numeric(row_dict, columns[i + 2])

        # Adiciona campos extras
        extra_fields = {}
        for col, value in row_dict.items():
            if col not in [date_col, municipality_col] and col != '_column_mapping':
                col_type = type_to_column.get(col)
                if not col_type or col_type not in ['new_cases', 'new_deaths', 'new_vaccinated',
                                                    'accumulated_cases', 'accumulated_deaths',
                                                    'accumulated_vaccinated']:
                    extra_fields[col] = value

        kwargs.update(extra_fields)

        return CovidData(date_value, municipality_value, **kwargs)

    def _safe_get_numeric(self, row_dict: Dict, column: str) -> int:
        """Obtém valor numérico de forma segura"""
        if not column or column not in row_dict:
            return 0

        value = str(row_dict[column]).strip()
        if not value:
            return 0

        # Remove caracteres não numéricos exceto ponto e vírgula
        cleaned_value = re.sub(r'[^\d\.,\-]', '', value)
        cleaned_value = cleaned_value.replace(',', '.')

        try:
            return int(float(cleaned_value))
        except (ValueError, TypeError):
            return 0

    def load_from_csv_file(self, file_path: str) -> bool:
        """Carrega dados diretamente de um arquivo CSV"""
        try:
            # Tenta diferentes codificações
            encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']

            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding, newline='') as file:
                        content = file.read()
                        if content.strip():
                            return self.load_data_from_text(content)
                except UnicodeDecodeError:
                    continue

            return False

        except Exception as e:
            print(f"Erro ao ler arquivo CSV: {e}")
            return False

    def export_to_csv(self, file_path: str) -> bool:
        """Exporta dados carregados para arquivo CSV"""
        try:
            with open(file_path, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)

                # Cabeçalho básico
                headers = [
                    'Data', 'Município', 'Novos Casos', 'Novos Óbitos',
                    'Novos Vacinados', 'Casos Acumulados', 'Óbitos Acumulados', 'Vacinados Acumulados'
                ]

                # Adiciona colunas extras se existirem
                if self.data and hasattr(self.data[0], 'extra_fields') and self.data[0].extra_fields:
                    extra_headers = list(self.data[0].extra_fields.keys())
                    headers.extend(extra_headers)

                writer.writerow(headers)

                # Dados
                for record in self.data:
                    row = [
                        record.date.strftime('%Y-%m-%d'),
                        record.municipality,
                        record.new_cases,
                        record.new_deaths,
                        record.new_vaccinated,
                        record.accumulated_cases,
                        record.accumulated_deaths,
                        record.accumulated_vaccinated
                    ]

                    # Adiciona campos extras
                    if hasattr(record, 'extra_fields') and record.extra_fields:
                        for key in record.extra_fields.keys():
                            row.append(record.extra_fields[key])

                    writer.writerow(row)

            return True
        except Exception as e:
            print(f"Erro ao exportar CSV: {e}")
            return False

    def get_monthly_summary(self) -> Dict[str, Dict[str, int]]:
        """Retorna resumo mensal dos dados"""
        monthly_data = {}

        for record in self.data:
            month_key = record.get_month_year()

            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'new_cases': 0,
                    'new_deaths': 0,
                    'new_vaccinated': 0,
                    'max_accumulated_cases': 0,
                    'max_accumulated_deaths': 0,
                    'max_accumulated_vaccinated': 0
                }

            monthly_data[month_key]['new_cases'] += record.new_cases
            monthly_data[month_key]['new_deaths'] += record.new_deaths
            monthly_data[month_key]['new_vaccinated'] += record.new_vaccinated
            monthly_data[month_key]['max_accumulated_cases'] = max(
                monthly_data[month_key]['max_accumulated_cases'],
                record.accumulated_cases
            )
            monthly_data[month_key]['max_accumulated_deaths'] = max(
                monthly_data[month_key]['max_accumulated_deaths'],
                record.accumulated_deaths
            )
            monthly_data[month_key]['max_accumulated_vaccinated'] = max(
                monthly_data[month_key]['max_accumulated_vaccinated'],
                record.accumulated_vaccinated
            )

        return monthly_data

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas gerais dos dados"""
        if not self.data:
            return {}

        total_cases = sum(record.new_cases for record in self.data)
        total_deaths = sum(record.new_deaths for record in self.data)
        total_vaccinated = sum(record.new_vaccinated for record in self.data)

        max_accumulated_cases = max((record.accumulated_cases for record in self.data), default=0)
        max_accumulated_deaths = max((record.accumulated_deaths for record in self.data), default=0)
        max_accumulated_vaccinated = max((record.accumulated_vaccinated for record in self.data), default=0)

        unique_municipalities = len(set(record.municipality for record in self.data))

        return {
            'total_records': len(self.data),
            'unique_municipalities': unique_municipalities,
            'date_range': f"{min(self.data, key=lambda x: x.date).date.strftime('%d/%m/%Y')} - "
                          f"{max(self.data, key=lambda x: x.date).date.strftime('%d/%m/%Y')}",
            'total_new_cases': total_cases,
            'total_new_deaths': total_deaths,
            'total_new_vaccinated': total_vaccinated,
            'max_accumulated_cases': max_accumulated_cases,
            'max_accumulated_deaths': max_accumulated_deaths,
            'max_accumulated_vaccinated': max_accumulated_vaccinated,
            'mortality_rate': (total_deaths / total_cases * 100) if total_cases > 0 else 0,
            'columns_detected': len(self.original_columns),
            'column_mapping': self.column_mapping
        }


class SimpleChart:
    """Classe para criar gráficos simples usando Canvas do Tkinter"""

    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.margin = 60

    def clear(self):
        """Limpa o canvas"""
        self.canvas.delete("all")

    def draw_bar_chart(self, data: Dict[str, int], title: str, max_value: Optional[int] = None):
        """Desenha gráfico de barras"""
        self.clear()

        if not data:
            self.canvas.create_text(
                self.canvas.winfo_width() // 2,
                self.canvas.winfo_height() // 2,
                text="Nenhum dado disponível",
                font=("Arial", 14)
            )
            return

        # Configurações
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        chart_width = canvas_width - 2 * self.margin
        chart_height = canvas_height - 2 * self.margin

        if max_value is None:
            max_value = max(data.values()) if data.values() else 1

        if max_value == 0:
            max_value = 1

        # Título
        self.canvas.create_text(
            canvas_width // 2, 20,
            text=title,
            font=("Arial", 12, "bold")
        )

        # Eixos
        self.canvas.create_line(
            self.margin, self.margin,
            self.margin, canvas_height - self.margin,
            width=2
        )

        self.canvas.create_line(
            self.margin, canvas_height - self.margin,
                         canvas_width - self.margin, canvas_height - self.margin,
            width=2
        )

        # Barras
        bar_width = chart_width // len(data)
        colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]

        for i, (label, value) in enumerate(data.items()):
            x1 = self.margin + i * bar_width + bar_width * 0.1
            x2 = self.margin + (i + 1) * bar_width - bar_width * 0.1

            bar_height = (value / max_value) * chart_height
            y1 = canvas_height - self.margin
            y2 = y1 - bar_height

            # Barra
            color = colors[i % len(colors)]
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline="black"
            )

            # Valor no topo da barra
            if bar_height > 20:
                self.canvas.create_text(
                    (x1 + x2) / 2, y2 - 10,
                    text=str(value),
                    font=("Arial", 8)
                )

            # Label no eixo X
            self.canvas.create_text(
                (x1 + x2) / 2, y1 + 15,
                text=label[:6] + "..." if len(label) > 6 else label,
                font=("Arial", 8),
                angle=45 if len(label) > 4 else 0
            )

        # Escala no eixo Y
        for i in range(5):
            y_pos = canvas_height - self.margin - (i / 4) * chart_height
            value = int((i / 4) * max_value)
            self.canvas.create_text(
                self.margin - 10, y_pos,
                text=str(value),
                font=("Arial", 8),
                anchor="e"
            )

    def draw_line_chart(self, data: Dict[str, int], title: str):
        """Desenha gráfico de linha"""
        self.clear()

        if not data or len(data) < 2:
            self.canvas.create_text(
                self.canvas.winfo_width() // 2,
                self.canvas.winfo_height() // 2,
                text="Dados insuficientes para gráfico de linha",
                font=("Arial", 14)
            )
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        chart_width = canvas_width - 2 * self.margin
        chart_height = canvas_height - 2 * self.margin

        max_value = max(data.values())
        if max_value == 0:
            max_value = 1

        # Título
        self.canvas.create_text(
            canvas_width // 2, 20,
            text=title,
            font=("Arial", 12, "bold")
        )

        # Eixos
        self.canvas.create_line(
            self.margin, self.margin,
            self.margin, canvas_height - self.margin,
            width=2
        )

        self.canvas.create_line(
            self.margin, canvas_height - self.margin,
                         canvas_width - self.margin, canvas_height - self.margin,
            width=2
        )

        # Pontos e linha
        points = list(data.items())
        step_x = chart_width / (len(points) - 1)

        prev_x = prev_y = None

        for i, (label, value) in enumerate(points):
            x = self.margin + i * step_x
            y = canvas_height - self.margin - (value / max_value) * chart_height

            # Ponto
            self.canvas.create_oval(
                x - 4, y - 4, x + 4, y + 4,
                fill="#e74c3c",
                outline="black"
            )

            # Linha conectando pontos
            if prev_x is not None and prev_y is not None:
                self.canvas.create_line(
                    prev_x, prev_y, x, y,
                    width=2,
                    fill="#3498db"
                )

            # Label
            if i % max(1, len(points) // 6) == 0:  # Mostrar apenas alguns labels
                self.canvas.create_text(
                    x, canvas_height - self.margin + 15,
                    text=label[:6],
                    font=("Arial", 8),
                    angle=45
                )

            prev_x, prev_y = x, y

        # Escala Y
        for i in range(5):
            y_pos = canvas_height - self.margin - (i / 4) * chart_height
            value = int((i / 4) * max_value)
            self.canvas.create_text(
                self.margin - 10, y_pos,
                text=str(value),
                font=("Arial", 8),
                anchor="e"
            )


class FlexibleMainApplication:
    """Aplicação principal com processamento flexível de CSV/TXT"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.processor = FlexibleDataProcessor()
        self.chart = None
        self.setup_ui()
        self.load_initial_data()

    def setup_ui(self):
        """Configura a interface do usuário"""
        self.root.title("COVID-19 Data Analyzer - Universal CSV/TXT Processor v2.0")
        self.root.geometry("1400x900")

        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame superior - controles
        control_frame = ttk.LabelFrame(main_frame, text="Controles e Arquivos", padding=10)
        control_frame.pack(fill="x", pady=(0, 10))

        # Primeira linha de botões
        button_frame1 = ttk.Frame(control_frame)
        button_frame1.pack(fill="x", pady=(0, 5))

        ttk.Button(button_frame1, text="📁 Carregar CSV",
                   command=self.load_csv_data).pack(side="left", padx=5)

        ttk.Button(button_frame1, text="📄 Carregar TXT/TSV",
                   command=self.load_txt_data).pack(side="left", padx=5)

        ttk.Button(button_frame1, text="💾 Exportar CSV",
                   command=self.export_csv_data).pack(side="left", padx=5)

        ttk.Button(button_frame1, text="📊 Estatísticas Detalhadas",
                   command=self.show_statistics).pack(side="left", padx=5)

        ttk.Button(button_frame1, text="🔍 Analisar Estrutura",
                   command=self.analyze_structure).pack(side="left", padx=5)

        # Segunda linha - seletor de gráfico
        button_frame2 = ttk.Frame(control_frame)
        button_frame2.pack(fill="x")

        ttk.Label(button_frame2, text="Tipo de Gráfico:").pack(side="left", padx=(0, 5))

        self.chart_type = ttk.Combobox(button_frame2, width=30, state="readonly")
        self.chart_type['values'] = [
            "Casos Novos por Mês (Barras)",
            "Óbitos Novos por Mês (Barras)",
            "Vacinados Novos por Mês (Barras)",
            "Casos Acumulados por Mês (Linha)",
            "Óbitos Acumulados por Mês (Linha)",
            "Vacinados Acumulados por Mês (Linha)",
            "Comparativo Casos vs Óbitos (Barras)",
            "Tendência Mensal (Linha)"
        ]
        self.chart_type.pack(side="left", padx=5)
        self.chart_type.set("Casos Novos por Mês (Barras)")

        ttk.Button(button_frame2, text="📈 Gerar Gráfico",
                   command=self.generate_chart).pack(side="left", padx=5)

        ttk.Button(button_frame2, text="🔄 Atualizar",
                   command=self.refresh_data).pack(side="left", padx=5)

        # Frame do meio - informações
        info_frame = ttk.LabelFrame(main_frame, text="Informações dos Dados Carregados", padding=10)
        info_frame.pack(fill="x", pady=(0, 10))

        self.info_label = ttk.Label(info_frame, text="Nenhum dado carregado", font=("Arial", 10))
        self.info_label.pack(anchor="w")

        # Frame de status/estrutura
        status_frame = ttk.LabelFrame(main_frame, text="Status e Compatibilidade", padding=10)
        status_frame.pack(fill="x", pady=(0, 10))

        status_text = (
            "✅ Suporte Universal: Qualquer ordem de colunas | "
            "✅ Detecção Automática: Delimitadores, cabeçalhos, tipos de dados | "
            "✅ Múltiplos Formatos: CSV, TSV, TXT, pipe-separated | "
            "✅ Codificação Flexível: UTF-8, Latin1, CP1252 | "
            "✅ Campos Opcionais: Funciona mesmo com dados incompletos"
        )
        ttk.Label(status_frame, text=status_text, wraplength=1200, font=("Arial", 9)).pack()

        # Frame inferior - gráfico
        chart_frame = ttk.LabelFrame(main_frame, text="Visualização de Dados", padding=10)
        chart_frame.pack(fill="both", expand=True)

        # Canvas para gráfico com scrollbar
        canvas_frame = ttk.Frame(chart_frame)
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="white", height=400)
        self.canvas.pack(fill="both", expand=True)

        # Aguarda o canvas ser renderizado para criar o objeto Chart
        self.canvas.after(100, self.init_chart)

    def init_chart(self):
        """Inicializa o objeto de gráfico após o canvas estar pronto"""
        self.chart = SimpleChart(self.canvas)
        # Gera um gráfico inicial se houver dados
        if self.processor.data:
            self.generate_chart()

    def load_csv_data(self):
        """Carrega dados de arquivo CSV com detecção automática de formato"""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo CSV/TSV de dados COVID-19",
            filetypes=[
                ("Todos os formatos suportados", "*.csv;*.tsv;*.txt"),
                ("Arquivos CSV", "*.csv"),
                ("Arquivos TSV", "*.tsv"),
                ("Arquivos TXT", "*.txt"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if file_path:
            if self.processor.load_from_csv_file(file_path):
                self.update_info_display()
                stats = self.processor.get_statistics()

                messagebox.showinfo("✅ Carregamento Bem-sucedido",
                                    f"Arquivo processado com sucesso!\n\n"
                                    f"📁 Arquivo: {file_path.split('/')[-1]}\n"
                                    f"📊 Registros: {len(self.processor.data):,}\n"
                                    f"🏛️ Municípios: {stats.get('unique_municipalities', 'N/A')}\n"
                                    f"📅 Período: {stats.get('date_range', 'N/A')}\n"
                                    f"📋 Colunas detectadas: {stats.get('columns_detected', 'N/A')}")

                if self.chart:
                    self.generate_chart()
            else:
                messagebox.showerror("❌ Erro de Processamento",
                                     "Não foi possível processar o arquivo.\n\n"
                                     "Verifique se:\n"
                                     "• O arquivo contém dados válidos\n"
                                     "• Pelo menos 2 colunas estão presentes\n"
                                     "• O formato é CSV, TSV ou TXT")

    def load_txt_data(self):
        """Carrega dados de arquivo TXT/TSV com máxima flexibilidade"""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo de texto com dados COVID-19",
            filetypes=[
                ("Arquivos de texto", "*.txt"),
                ("Arquivos TSV", "*.tsv"),
                ("Arquivos de dados", "*.dat"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if file_path:
            encodings_tried = []
            content = None

            # Tenta múltiplas codificações
            for encoding in ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                        encodings_tried.append(f"✅ {encoding}")
                        break
                except UnicodeDecodeError:
                    encodings_tried.append(f"❌ {encoding}")
                    continue
                except Exception as e:
                    encodings_tried.append(f"❌ {encoding} ({str(e)})")
                    continue

            if content and self.processor.load_data_from_text(content):
                self.update_info_display()
                stats = self.processor.get_statistics()

                messagebox.showinfo("✅ Texto Processado",
                                    f"Arquivo de texto carregado!\n\n"
                                    f"📁 Arquivo: {file_path.split('/')[-1]}\n"
                                    f"📊 Registros: {len(self.processor.data):,}\n"
                                    f"🔤 Codificação usada: {encodings_tried[-1]}\n"
                                    f"📋 Colunas: {stats.get('columns_detected', 'N/A')}")

                if self.chart:
                    self.generate_chart()
            else:
                messagebox.showerror("❌ Erro de Leitura",
                                     f"Não foi possível ler o arquivo.\n\n"
                                     f"Codificações tentadas:\n" + "\n".join(encodings_tried))

    def export_csv_data(self):
        """Exporta dados atuais para arquivo CSV"""
        if not self.processor.data:
            messagebox.showwarning("⚠️ Aviso", "Nenhum dado disponível para exportar")
            return

        file_path = filedialog.asksaveasfilename(
            title="Salvar dados processados como CSV",
            defaultextension=".csv",
            filetypes=[
                ("Arquivo CSV", "*.csv"),
                ("Arquivo TSV", "*.tsv"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if file_path:
            if self.processor.export_to_csv(file_path):
                stats = self.processor.get_statistics()
                messagebox.showinfo("💾 Exportação Concluída",
                                    f"Dados exportados com sucesso!\n\n"
                                    f"📁 Arquivo: {file_path.split('/')[-1]}\n"
                                    f"📊 Registros exportados: {len(self.processor.data):,}\n"
                                    f"📋 Formato: CSV UTF-8")
            else:
                messagebox.showerror("❌ Erro de Exportação", "Erro ao salvar o arquivo CSV")

    def analyze_structure(self):
        """Analisa e mostra a estrutura dos dados carregados"""
        if not self.processor.data:
            messagebox.showwarning("⚠️ Aviso", "Nenhum dado carregado para analisar")
            return

        # Cria janela de análise
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("🔍 Análise de Estrutura dos Dados")
        analysis_window.geometry("900x700")

        # Frame principal com scroll
        canvas = tk.Canvas(analysis_window)
        scrollbar = ttk.Scrollbar(analysis_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Análise de colunas originais
        columns_frame = ttk.LabelFrame(scrollable_frame, text="📋 Colunas Detectadas", padding=10)
        columns_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(columns_frame, text=f"Total de colunas: {len(self.processor.original_columns)}",
                  font=("Arial", 10, "bold")).pack(anchor="w")

        for i, col in enumerate(self.processor.original_columns):
            col_type = self.processor.column_mapping.get(col, "Não mapeada")
            ttk.Label(columns_frame, text=f"{i + 1}. {col} → {col_type}").pack(anchor="w", padx=20)

        # Análise de mapeamento
        mapping_frame = ttk.LabelFrame(scrollable_frame, text="🔗 Mapeamento de Dados", padding=10)
        mapping_frame.pack(fill="x", padx=10, pady=5)

        mapping_info = {
            'date': 'Data dos registros',
            'municipality': 'Nome do município/localidade',
            'new_cases': 'Novos casos registrados',
            'new_deaths': 'Novos óbitos registrados',
            'new_vaccinated': 'Novos vacinados',
            'accumulated_cases': 'Total acumulado de casos',
            'accumulated_deaths': 'Total acumulado de óbitos',
            'accumulated_vaccinated': 'Total acumulado de vacinados'
        }

        reverse_mapping = {v: k for k, v in self.processor.column_mapping.items()}

        for field_type, description in mapping_info.items():
            original_column = reverse_mapping.get(field_type, "❌ Não encontrado")
            status = "✅" if original_column != "❌ Não encontrado" else "❌"
            ttk.Label(mapping_frame, text=f"{status} {description}: {original_column}").pack(anchor="w")

        # Amostra de dados
        sample_frame = ttk.LabelFrame(scrollable_frame, text="📊 Amostra dos Dados (Primeiros 5 registros)", padding=10)
        sample_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Tabela com amostra
        tree = ttk.Treeview(sample_frame, height=6)
        tree.pack(fill="both", expand=True)

        # Define colunas
        display_columns = ['Data', 'Município', 'Novos Casos', 'Novos Óbitos', 'Casos Acum.', 'Óbitos Acum.']
        tree['columns'] = display_columns
        tree['show'] = 'headings'

        for col in display_columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        # Adiciona dados de amostra
        for i, record in enumerate(self.processor.data[:5]):
            tree.insert('', 'end', values=(
                record.date.strftime('%d/%m/%Y'),
                record.municipality,
                record.new_cases,
                record.new_deaths,
                record.accumulated_cases,
                record.accumulated_deaths
            ))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_initial_data(self):
        """Carrega os dados iniciais fornecidos como exemplo"""
        initial_data = """2025-01-08	Aracaju	15	1	4	1500	89	9661
2025-01-09	Aracaju	3	0	2	1503	89	9663
2025-01-10	Aracaju	22	0	5	1525	89	9668
2025-01-11	Aracaju	7	0	3	1532	89	9671
2025-01-12	Aracaju	8	1	6	1540	90	9677
2025-01-13	Aracaju	13	0	4	1553	90	9681
2025-01-14	Aracaju	0	1	7	1553	91	9688
2025-01-15	Aracaju	7	1	4	1560	92	9692
2025-02-01	Aracaju	11	0	6	1718	98	9773
2025-02-15	Aracaju	17	0	5	1867	105	9838
2025-03-01	Aracaju	12	1	2	2028	110	9918
2025-03-15	Aracaju	5	0	9	2155	115	9993
2025-04-01	Aracaju	6	0	10	2317	126	10098
2025-04-15	Aracaju	11	1	7	2453	134	10168
2025-05-01	Aracaju	8	0	6	2611	141	10234
2025-05-15	Aracaju	12	1	0	2725	146	10310
2025-06-01	Aracaju	15	0	8	2903	153	10379
2025-06-15	Aracaju	2	0	5	3030	160	10432
2025-07-01	Aracaju	3	1	5	3160	166	10484
2025-07-15	Aracaju	12	0	8	3295	171	10558
2025-07-31	Aracaju	13	1	6	3480	178	10611"""

        if self.processor.load_data_from_text(initial_data):
            self.update_info_display()
            print("✅ Dados de exemplo carregados com sucesso!")
        else:
            print("❌ Erro ao carregar dados de exemplo")

    def update_info_display(self):
        """Atualiza as informações exibidas na interface"""
        if not self.processor.data:
            self.info_label.config(text="Nenhum dado carregado")
            return

        stats = self.processor.get_statistics()
        info_text = (
            f"📊 Registros: {stats['total_records']:,} | "
            f"🏛️ Municípios: {stats['unique_municipalities']} | "
            f"📅 Período: {stats['date_range']} | "
            f"📈 Novos casos: {stats['total_new_cases']:,} | "
            f"💀 Novos óbitos: {stats['total_new_deaths']:,} | "
            f"📋 Colunas: {stats['columns_detected']} | "
            f"💊 Taxa mortalidade: {stats['mortality_rate']:.2f}%"
        )
        self.info_label.config(text=info_text)

    def refresh_data(self):
        """Atualiza a exibição de dados e gráficos"""
        self.update_info_display()
        if self.chart and self.processor.data:
            self.generate_chart()

    def show_statistics(self):
        """Mostra estatísticas detalhadas em uma janela separada"""
        if not self.processor.data:
            messagebox.showwarning("⚠️ Aviso", "Nenhum dado carregado para mostrar estatísticas")
            return

        stats = self.processor.get_statistics()
        monthly_summary = self.processor.get_monthly_summary()

        # Cria janela de estatísticas
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Estatísticas Detalhadas - COVID-19")
        stats_window.geometry("1000x700")

        # Notebook para abas
        notebook = ttk.Notebook(stats_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Aba 1: Estatísticas Gerais
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="📈 Estatísticas Gerais")

        stats_content = ttk.LabelFrame(general_frame, text="Resumo Geral", padding=20)
        stats_content.pack(fill="both", expand=True, padx=10, pady=10)

        stats_text = [
            f"📊 Total de registros processados: {stats['total_records']:,}",
            f"🏛️ Municípios únicos: {stats['unique_municipalities']}",
            f"📅 Período dos dados: {stats['date_range']}",
            f"📈 Total de novos casos: {stats['total_new_cases']:,}",
            f"💀 Total de novos óbitos: {stats['total_new_deaths']:,}",
            f"💉 Total de novos vacinados: {stats['total_new_vaccinated']:,}",
            f"🔺 Máximo de casos acumulados: {stats['max_accumulated_cases']:,}",
            f"🔺 Máximo de óbitos acumulados: {stats['max_accumulated_deaths']:,}",
            f"🔺 Máximo de vacinados acumulados: {stats['max_accumulated_vaccinated']:,}",
            f"📊 Taxa de mortalidade: {stats['mortality_rate']:.3f}%",
            f"📋 Total de colunas detectadas: {stats['columns_detected']}"
        ]

        for stat in stats_text:
            ttk.Label(stats_content, text=stat, font=("Arial", 11)).pack(anchor="w", pady=2)

        # Aba 2: Resumo Mensal
        monthly_frame = ttk.Frame(notebook)
        notebook.add(monthly_frame, text="📅 Resumo Mensal")

        # Tabela mensal
        monthly_content = ttk.LabelFrame(monthly_frame, text="Dados por Mês", padding=10)
        monthly_content.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ('Mês/Ano', 'Novos Casos', 'Novos Óbitos', 'Novos Vacinados',
                   'Max Casos Acum.', 'Max Óbitos Acum.', 'Max Vacinados Acum.')
        tree = ttk.Treeview(monthly_content, columns=columns, show='headings', height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=140)

        for month, data in sorted(monthly_summary.items()):
            tree.insert('', 'end', values=(
                month,
                f"{data['new_cases']:,}",
                f"{data['new_deaths']:,}",
                f"{data['new_vaccinated']:,}",
                f"{data['max_accumulated_cases']:,}",
                f"{data['max_accumulated_deaths']:,}",
                f"{data['max_accumulated_vaccinated']:,}"
            ))

        tree.pack(fill="both", expand=True)

        # Scrollbars para a tabela
        v_scroll = ttk.Scrollbar(monthly_content, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side="right", fill="y")

        h_scroll = ttk.Scrollbar(monthly_content, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=h_scroll.set)
        h_scroll.pack(side="bottom", fill="x")

        # Aba 3: Estrutura dos Dados
        structure_frame = ttk.Frame(notebook)
        notebook.add(structure_frame, text="🔍 Estrutura")

        struct_content = ttk.LabelFrame(structure_frame, text="Mapeamento de Colunas", padding=15)
        struct_content.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(struct_content, text="Mapeamento automático realizado:",
                  font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))

        for original_col, mapped_type in stats['column_mapping'].items():
            ttk.Label(struct_content, text=f"• {original_col} → {mapped_type}",
                      font=("Arial", 10)).pack(anchor="w", padx=20)

    def generate_chart(self):
        """Gera gráfico baseado na seleção do usuário"""
        if not self.processor.data or not self.chart:
            return

        chart_selection = self.chart_type.get()
        monthly_summary = self.processor.get_monthly_summary()

        if not monthly_summary:
            return

        try:
            if "Casos Novos" in chart_selection:
                data = {month: summary['new_cases'] for month, summary in sorted(monthly_summary.items())}
                self.chart.draw_bar_chart(data, "📈 Novos Casos por Mês")

            elif "Óbitos Novos" in chart_selection:
                data = {month: summary['new_deaths'] for month, summary in sorted(monthly_summary.items())}
                self.chart.draw_bar_chart(data, "💀 Novos Óbitos por Mês")

            elif "Vacinados Novos" in chart_selection:
                data = {month: summary['new_vaccinated'] for month, summary in sorted(monthly_summary.items())}
                self.chart.draw_bar_chart(data, "💉 Novos Vacinados por Mês")

            elif "Casos Acumulados" in chart_selection:
                data = {month: summary['max_accumulated_cases'] for month, summary in sorted(monthly_summary.items())}
                self.chart.draw_line_chart(data, "📊 Casos Acumulados por Mês")

            elif "Óbitos Acumulados" in chart_selection:
                data = {month: summary['max_accumulated_deaths'] for month, summary in sorted(monthly_summary.items())}
                self.chart.draw_line_chart(data, "📉 Óbitos Acumulados por Mês")

            elif "Vacinados Acumulados" in chart_selection:
                data = {month: summary['max_accumulated_vaccinated'] for month, summary in
                        sorted(monthly_summary.items())}
                self.chart.draw_line_chart(data, "💉 Vacinados Acumulados por Mês")

            elif "Comparativo" in chart_selection:
                data = {}
                for month, summary in sorted(monthly_summary.items()):
                    data[f"{month}(C)"] = summary['new_cases']
                    data[f"{month}(O)"] = summary['new_deaths']
                self.chart.draw_bar_chart(data, "⚖️ Casos vs Óbitos por Mês")

            elif "Tendência" in chart_selection:
                data = {month: summary['new_cases'] + summary['new_deaths'] for month, summary in
                        sorted(monthly_summary.items())}
                self.chart.draw_line_chart(data, "📈 Tendência Geral (Casos + Óbitos)")

        except Exception as e:
            print(f"Erro ao gerar gráfico: {e}")
            messagebox.showerror("Erro", f"Erro ao gerar gráfico: {str(e)}")


def main():
    """Função principal da aplicação"""
    root = tk.Tk()

    # Configura ícone se disponível
    try:
        root.iconbitmap('covid_icon.ico')
    except:
        pass

    app = FlexibleMainApplication(root)

    # Centraliza a janela
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":
    main()