package br.covidsergipe.service;

import br.covidsergipe.model.*;
import java.util.*;

public class AnaliseCovid {
    private final List<RegistroCovid> registros;

    public AnaliseCovid(List<RegistroCovid> registros) {
        this.registros = registros;
        Collections.sort(this.registros, (r1, r2) -> r1.getData().compareTo(r2.getData()));
    }

    public int getTotalCasosEstado() {
        int maior = 0;
        for (RegistroCovid r : registros) {
            if (r.getTipoLocal().equalsIgnoreCase("state")) {
                if (r.getCasos() > maior) {
                    maior = r.getCasos();
                }
            }
        }
        return maior;
    }

    public int getTotalObitosEstado() {
        int maior = 0;
        for (RegistroCovid r : registros) {
            if (r.getTipoLocal().equalsIgnoreCase("state")) {
                if (r.getObitos() > maior) {
                    maior = r.getObitos();
                }
            }
        }
        return maior;
    }

    public Map<String, Integer> getNovosCasosEstado() {
        Map<String, Integer> novosCasos = new LinkedHashMap<>();
        int casosAnterior = 0;
        for (RegistroCovid r : registros) {
            if (r.getTipoLocal().equalsIgnoreCase("state")) {
                int novos = r.getCasos() - casosAnterior;
                casosAnterior = r.getCasos();
                novosCasos.put(r.getData(), novos);
            }
        }
        return novosCasos;
    }

    public Map<String, Integer> getNovosObitosEstado() {
        Map<String, Integer> novosObitos = new LinkedHashMap<>();
        int obitosAnterior = 0;
        for (RegistroCovid r : registros) {
            if (r.getTipoLocal().equalsIgnoreCase("state")) {
                int novos = r.getObitos() - obitosAnterior;
                obitosAnterior = r.getObitos();
                novosObitos.put(r.getData(), novos);
            }
        }
        return novosObitos;
    }

    public Map<String, Integer> getNovosCasosMes() {
        Map<String, Integer> novosCasos = new TreeMap<>();
        int casosAnterior = 0;
        for (RegistroCovid r : registros) {
            if (r.getTipoLocal().equalsIgnoreCase("state")) {
                String mes = r.getData().substring(0, 7);
                int novos = r.getCasos() - casosAnterior;
                casosAnterior = r.getCasos();
                novosCasos.put(mes, novosCasos.getOrDefault(mes, 0) + novos);
            }
        }
        return novosCasos;
    }

    public Map<String, Integer> getNovosObitosMes() {
        Map<String, Integer> novosObitos = new TreeMap<>();
        int obitosAnterior = 0;
        for (RegistroCovid r : registros) {
            if (r.getTipoLocal().equalsIgnoreCase("state")) {
                String mes = r.getData().substring(0, 7);
                int novos = r.getObitos() - obitosAnterior;
                obitosAnterior = r.getObitos();
                novosObitos.put(mes, novosObitos.getOrDefault(mes, 0) + novos);
            }
        }
        return novosObitos;
    }

    public Map<String, Integer> getCasosAcumuladosMes() {
        Map<String, Integer> casosAcumulados = new TreeMap<>();
        for (RegistroCovid r : registros) {
            if (r.getTipoLocal().equalsIgnoreCase("state")) {
                String mes = r.getData().substring(0, 7);
                casosAcumulados.put(mes, r.getCasos());
            }
        }
        return casosAcumulados;
    }

    public Map<String, Integer> getObitosAcumuladosMes() {
        Map<String, Integer> obitosAcumulados = new TreeMap<>();
        for (RegistroCovid r : registros) {
            if (r.getTipoLocal().equalsIgnoreCase("state")) {
                String mes = r.getData().substring(0, 7);
                obitosAcumulados.put(mes, r.getObitos());
            }
        }
        return obitosAcumulados;
    }

    public Map<String, Integer> getTendenciaMensal() {
        Map<String, Integer> tendencia = new TreeMap<>();
        Map<String, Integer> acumulados = getCasosAcumuladosMes();
        String mesAnterior = null;
        int casosAnterior = 0;

        for (Map.Entry<String, Integer> entry : acumulados.entrySet()) {
            String mes = entry.getKey();
            int casos = entry.getValue();
            if (mesAnterior != null) {
                int diferenca = casos - casosAnterior;
                tendencia.put(mes, diferenca);
            }
            mesAnterior = mes;
            casosAnterior = casos;
        }
        return tendencia;
    }

        public double getTaxaMortalidadeAtual() {
        double taxa = 0.0;
        for (RegistroCovid r : registros) {
            if (r.getTipoLocal().equalsIgnoreCase("state")) {
                taxa = r.getTaxaMortalidade(); 
            }
        }
        return taxa;
    }

    public double getCasos100MilAtual() {
        double casos100k = 0.0;
        for (RegistroCovid r : registros) {
            if (r.getTipoLocal().equalsIgnoreCase("state")) {
                casos100k = r.getConfirmados100k();
            }
        }
        return casos100k;
    }

    public Map<String, Integer> getCasosTotaisMunicipio() {
        Map<String, Integer> casosPorMunicipio = new HashMap<>();
        for (RegistroCovid r : registros) {
            if (r.getTipoLocal().equalsIgnoreCase("city")) {
                casosPorMunicipio.put(r.getMunicipio(), r.getCasos());
            }
        }
        return casosPorMunicipio;
    }
    
    public Map<String, Integer> getObitosTotaisMunicipio() {
        Map<String, Integer> obitosPorMunicipio = new HashMap<>();
        for (RegistroCovid r : registros) {
            if (r.getTipoLocal().equalsIgnoreCase("city")) {
                obitosPorMunicipio.put(r.getMunicipio(), r.getObitos());
            }
        }
        return obitosPorMunicipio;
    }

    public Map<String, Double> getTaxaMortalidadePorMunicipio() {
        Map<String, Double> mortalidade = new HashMap<>();
        for (RegistroCovid r : registros) {
            if (r.getTipoLocal().equalsIgnoreCase("city")) {
                mortalidade.put(r.getMunicipio(), r.getTaxaMortalidade());
            }
        }
        return mortalidade;
    }

}
