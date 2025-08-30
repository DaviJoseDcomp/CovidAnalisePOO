package br.covidsergipe.ui;

import br.covidsergipe.model.*;
import br.covidsergipe.service.*;
import java.awt.*;
import java.io.File;
import java.util.List;
import javax.swing.*;

public class AnaliseCovidGUI extends JFrame {
    private JComboBox<String> comboBox;
    private PainelGrafico painel;
    private AnaliseCovid analise;
    private JLabel lResumo;

    public AnaliseCovidGUI() {
        setTitle("Análise COVID Sergipe");
        setSize(900, 650);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        // Painel superior com informações e controles
        JPanel painelTopo = new JPanel(new BorderLayout());
        
        // Painel de controles
        JPanel painelControles = new JPanel(new FlowLayout());
        JButton btnCarregar = new JButton("Carregar CSV");
        JButton btnDetalhes = new JButton("Estatísticas Detalhadas");

        comboBox = new JComboBox<>(new String[]{
            "Casos novos por mês",
            "Óbitos novos por mês",
            "Casos acumulados por mês",
            "Óbitos acumulados por mês",
            "Comparativo casos vs óbitos",
            "Tendência mensal de casos",
            "Top 5 municípios (casos)",
            "Top 5 municípios (óbitos)"
        });

        painelControles.add(btnCarregar);
        painelControles.add(comboBox);
        painelControles.add(btnDetalhes);

        // Label para resumo das informações
        lResumo = new JLabel("Carregue um arquivo CSV para visualizar os dados.");
        lResumo.setHorizontalAlignment(SwingConstants.CENTER);
        lResumo.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        lResumo.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 12));

        painelTopo.add(painelControles, BorderLayout.NORTH);
        painelTopo.add(lResumo, BorderLayout.CENTER);

        painel = new PainelGrafico();

        add(painelTopo, BorderLayout.NORTH);
        add(painel, BorderLayout.CENTER);

        btnCarregar.addActionListener(_ -> {
            JFileChooser chooser = new JFileChooser();
            int resultado = chooser.showOpenDialog(AnaliseCovidGUI.this);
            if (resultado == JFileChooser.APPROVE_OPTION) {
                File arquivo = chooser.getSelectedFile();
                List<RegistroCovid> registros = LeitorRegistro.lerArquivo(arquivo.getAbsolutePath());
                analise = new AnaliseCovid(registros);
                painel.setAnalise(analise);
                painel.setGraficoSelecionado(comboBox.getSelectedIndex());
                painel.repaint();

                lResumo.setText(String.format(
                    "Total registros: %d | Casos: %d | Óbitos: %d | Mortalidade: %.2f%% | Casos por 100k hab.: %.2f",
                    registros.size(),
                    analise.getTotalCasosEstado(),
                    analise.getTotalObitosEstado(),
                    analise.getTaxaMortalidadeAtual(),
                    analise.getCasos100MilAtual()
                ));
            }
        });
        
        comboBox.addActionListener(_ -> {
            if (analise != null) {
                painel.setGraficoSelecionado(comboBox.getSelectedIndex());
                painel.repaint();
            }
        });

        btnDetalhes.addActionListener(_ -> {
            if (analise == null) {
                JOptionPane.showMessageDialog(this, "Carregue primeiro um arquivo CSV!", 
                    "Erro", JOptionPane.WARNING_MESSAGE);
                return;
            }
            
            StringBuilder texto = new StringBuilder();
            // Adiciona cabeçalho explicativo
            texto.append("=== ESTATÍSTICAS DETALHADAS - COVID-19 SERGIPE ===\n\n");
            texto.append("Formato dos dados:\n");
            texto.append("DATA | ESTADO | CIDADE | TIPO_DE_LOCAL | POPULAÇÃO_ESTIMADA | CASOS | ");
            texto.append("CONFIRMADOS_POR_100K_HABITANTES | ÓBITOS | TAXA_DE_MORTALIDADE\n");
            texto.append("").append("-".repeat(100)).append("\n\n");
            
            // Adiciona os dados dos registros
            for (RegistroCovid r : analise.getRegistros()) {
                texto.append(r.toString()).append("\n");
            }
            
            JTextArea textArea = new JTextArea(texto.toString());
            textArea.setEditable(false);
            textArea.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 12));
            JScrollPane scrollPane = new JScrollPane(textArea);
            scrollPane.setPreferredSize(new Dimension(800, 500));
            
            JOptionPane.showMessageDialog(this, scrollPane, "Estatísticas Detalhadas", 
                JOptionPane.INFORMATION_MESSAGE);
        });
    }
}