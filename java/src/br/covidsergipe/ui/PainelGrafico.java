package br.covidsergipe.ui;

import br.covidsergipe.service.*;
import java.awt.*;
import java.util.*;
import javax.swing.*;

public class PainelGrafico extends JPanel {
    private AnaliseCovid analise;
    private int graficoSelecionado = 0;

    public void setAnalise(AnaliseCovid analise) {
        this.analise = analise;
    }

    public void setGraficoSelecionado(int index) {
        this.graficoSelecionado = index;
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);

        if (analise == null) {
            g.drawString("Carregue um arquivo CSV para visualizar os gráficos", 20, 20);
            return;
        }

        Graphics2D g2 = (Graphics2D) g;
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        int largura = getWidth() - 120;
        int altura = getHeight() - 120;
        int x0 = 60;
        int y0 = getHeight() - 70;

        // Fundo dos eixos
        g2.drawLine(x0, y0, x0 + largura, y0); // eixo X
        g2.drawLine(x0, y0, x0, y0 - altura); // eixo Y

        switch (graficoSelecionado) {
            case 0 -> // Casos novos por mês
                desenharBarras(g2, analise.getNovosCasosMes(), "Casos novos");
            case 1 -> // Óbitos novos por mês
                desenharBarras(g2, analise.getNovosObitosMes(), "Óbitos novos");
            case 2 -> // Casos acumulados por mês
                desenharLinha(g2, analise.getCasosAcumuladosMes(), "Casos acumulados");
            case 3 -> // Óbitos acumulados por mês
                desenharLinha(g2, analise.getObitosAcumuladosMes(), "Óbitos acumulados");
            case 4 -> // Comparativo casos vs óbitos
                desenharComparativo(g2, analise.getCasosAcumuladosMes(), analise.getObitosAcumuladosMes());
            case 5 -> // Tendência mensal de casos
                desenharLinha(g2, analise.getTendenciaMensal(), "Tendência casos");
            case 6 -> // Top 5 municípios (casos)
                desenharTopMunicipios(g2, analise.getCasosTotaisMunicipio(), "Casos");
            case 7 -> // Top 5 municípios (óbitos)
                desenharTopMunicipios(g2, analise.getObitosTotaisMunicipio(), "Óbitos");
        }
    }

    private void desenharBarras(Graphics2D g2, Map<String, Integer> dados, String titulo) {
        if (dados.isEmpty()) return;
        
        int larguraDisponivel = getWidth() - 120;
        int numBarras = dados.size();
        int espacamento = Math.max(50, larguraDisponivel / (numBarras + 1));
        int larguraBarra = Math.min(40, espacamento - 10);
        
        int x = 60 + espacamento / 2;
        int max = Collections.max(dados.values());
        int alturaMaxima = getHeight() - 150;

        for (Map.Entry<String, Integer> entry : dados.entrySet()) {
            if (x + larguraBarra > getWidth() - 60) break; // Para se passar da borda
            
            int altura = (int) ((entry.getValue() / (double) max) * alturaMaxima);
            int y = getHeight() - 70 - altura;
            
            g2.setColor(Color.BLUE);
            g2.fillRect(x, y, larguraBarra, altura);
            
            // Mostra o valor acima da barra
            g2.setColor(Color.BLACK);
            String valor = String.format("%,d", entry.getValue());
            FontMetrics fm = g2.getFontMetrics();
            int larguraTexto = fm.stringWidth(valor);
            g2.drawString(valor, x + (larguraBarra - larguraTexto) / 2, y - 5);
            
            // Mostra a data abaixo da barra
            String data = entry.getKey();
            int larguraData = fm.stringWidth(data);
            g2.drawString(data, x + (larguraBarra - larguraData) / 2, getHeight() - 50);
            x += espacamento;
        }
        g2.drawString(titulo, 60, 30);
    }

    private void desenharLinha(Graphics2D g2, Map<String, Integer> dados, String titulo) {
        if (dados.isEmpty()) return;
        
        int larguraDisponivel = getWidth() - 120;
        int numPontos = dados.size();
        int passo = Math.max(40, larguraDisponivel / numPontos);
        
        int x = 60 + passo / 2;
        int max = Collections.max(dados.values());
        int min = Collections.min(dados.values());
        int alturaMaxima = getHeight() - 150;
        int anteriorX = -1, anteriorY = -1;

        // Desenha escalas do eixo Y
        desenharEscalaY(g2, min, max, alturaMaxima);

        for (Map.Entry<String, Integer> entry : dados.entrySet()) {
            if (x > getWidth() - 60) break; // Para se passar da borda
            
            int y = getHeight() - 70 - (int) ((entry.getValue() - min) / (double) (max - min) * alturaMaxima);
            g2.setColor(Color.BLUE);
            g2.fillOval(x - 4, y - 4, 8, 8);
            
            if (anteriorX != -1) {
                g2.drawLine(anteriorX, anteriorY, x, y);
            }
            anteriorX = x;
            anteriorY = y;
            
            // Mostra a data no eixo X
            g2.setColor(Color.BLACK);
            FontMetrics fm = g2.getFontMetrics();
            String data = entry.getKey();
            int larguraData = fm.stringWidth(data);
            g2.drawString(data, x - larguraData / 2, getHeight() - 50);
            x += passo;
        }
        g2.drawString(titulo, 60, 30);
    }

    private void desenharEscalaY(Graphics2D g2, int min, int max, int alturaMaxima) {
        int numDivisoes = 5;
        int intervalo = (max - min) / numDivisoes;
        
        for (int i = 0; i <= numDivisoes; i++) {
            int valor = min + (i * intervalo);
            int y = getHeight() - 70 - (int) ((valor - min) / (double) (max - min) * alturaMaxima);
            
            // Linha guia
            g2.setColor(Color.LIGHT_GRAY);
            g2.drawLine(60, y, getWidth() - 60, y);
            
            // Valor no eixo Y
            g2.setColor(Color.BLACK);
            String valorTexto = String.format("%,d", valor);
            FontMetrics fm = g2.getFontMetrics();
            g2.drawString(valorTexto, 60 - fm.stringWidth(valorTexto) - 5, y + 4);
        }
    }

    private void desenharComparativo(Graphics2D g2, Map<String, Integer> casos, Map<String, Integer> obitos) {
        if (casos.isEmpty()) return;
        
        int larguraDisponivel = getWidth() - 120;
        int numGrupos = casos.size();
        int espacamento = Math.max(60, larguraDisponivel / numGrupos);
        int larguraBarra = Math.min(20, (espacamento - 10) / 2);
        
        int x = 60 + espacamento / 2 - larguraBarra;
        int max = Math.max(Collections.max(casos.values()), Collections.max(obitos.values()));
        int alturaMaxima = getHeight() - 150;

        for (String mes : casos.keySet()) {
            if (x + larguraBarra * 2 + 5 > getWidth() - 60) break; // Para se passar da borda
            
            int alturaCasos = (int) ((casos.get(mes) / (double) max) * alturaMaxima);
            int alturaObitos = (int) ((obitos.get(mes) / (double) max) * alturaMaxima);

            int yCasos = getHeight() - 70 - alturaCasos;
            int yObitos = getHeight() - 70 - alturaObitos;

            // Barra de casos (azul)
            g2.setColor(Color.BLUE);
            g2.fillRect(x, yCasos, larguraBarra, alturaCasos);
            
            // Valor acima da barra de casos
            g2.setColor(Color.BLACK);
            String valorCasos = String.format("%,d", casos.get(mes));
            FontMetrics fm = g2.getFontMetrics();
            int larguraTextoCasos = fm.stringWidth(valorCasos);
            g2.drawString(valorCasos, x + (larguraBarra - larguraTextoCasos) / 2, yCasos - 5);

            // Barra de óbitos (vermelho)
            g2.setColor(Color.RED);
            g2.fillRect(x + larguraBarra + 5, yObitos, larguraBarra, alturaObitos);
            
            // Valor acima da barra de óbitos
            g2.setColor(Color.BLACK);
            String valorObitos = String.format("%,d", obitos.get(mes));
            int larguraTextoObitos = fm.stringWidth(valorObitos);
            g2.drawString(valorObitos, x + larguraBarra + 5 + (larguraBarra - larguraTextoObitos) / 2, yObitos - 5);

            // Data abaixo das barras (centralizada)
            String data = mes;
            int larguraData = fm.stringWidth(data);
            g2.drawString(data, x + larguraBarra - larguraData / 2, getHeight() - 50);
            x += espacamento;
        }
        
        // Legenda
        g2.setColor(Color.BLUE);
        g2.fillRect(60, 50, 15, 10);
        g2.setColor(Color.BLACK);
        g2.drawString("Casos", 80, 60);
        
        g2.setColor(Color.RED);
        g2.fillRect(130, 50, 15, 10);
        g2.setColor(Color.BLACK);
        g2.drawString("Óbitos", 150, 60);
        
        g2.drawString("Casos vs Óbitos", 60, 30);
    }

    private void desenharTopMunicipios(Graphics2D g2, Map<String, Integer> dados, String titulo) {
        java.util.List<Map.Entry<String, Integer>> lista = new ArrayList<>(dados.entrySet());
        lista.sort((a, b) -> b.getValue() - a.getValue());
        lista = lista.subList(0, Math.min(5, lista.size()));

        if (lista.isEmpty()) return;
        
        int larguraDisponivel = getWidth() - 120;
        int numBarras = lista.size();
        int espacamento = Math.max(80, larguraDisponivel / numBarras);
        int larguraBarra = Math.min(60, espacamento - 20);
        
        int x = 60 + espacamento / 2 - larguraBarra / 2;
        int max = lista.get(0).getValue();
        int alturaMaxima = getHeight() - 150;

        for (Map.Entry<String, Integer> entry : lista) {
            if (x + larguraBarra > getWidth() - 60) break; // Para se passar da borda
            
            int altura = (int) ((entry.getValue() / (double) max) * alturaMaxima);
            int y = getHeight() - 70 - altura;
            
            g2.setColor(Color.BLUE);
            g2.fillRect(x, y, larguraBarra, altura);
            
            // Mostra o valor acima da barra
            g2.setColor(Color.BLACK);
            String valor = String.format("%,d", entry.getValue());
            FontMetrics fm = g2.getFontMetrics();
            int larguraTexto = fm.stringWidth(valor);
            g2.drawString(valor, x + (larguraBarra - larguraTexto) / 2, y - 5);
            
            // Nome do município abaixo da barra
            String municipio = entry.getKey();
            if (municipio.length() > 10) {
                municipio = municipio.substring(0, 8) + "...";
            }
            int larguraMunicipio = fm.stringWidth(municipio);
            g2.drawString(municipio, x + (larguraBarra - larguraMunicipio) / 2, getHeight() - 50);
            
            x += espacamento;
        }
        g2.drawString("Top 5 municípios - " + titulo, 60, 30);
    }
}