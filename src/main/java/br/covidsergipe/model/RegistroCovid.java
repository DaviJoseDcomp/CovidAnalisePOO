package br.covidsergipe.model;

public class RegistroCovid {

    private final String data;
    private final String estado;
    private final String municipio;
    private final String tipoLocal;
    private final int casos;
    private final int obitos;
    private final String ultimoRegistro;
    private final int populacao;
    private final int codigoMunicipio;
    private final double confirmados100k;
    private final double taxaMortalidade;

    public RegistroCovid(String data, String estado, String municipio, String tipoLocal, int casos, int obitos, String ultimoRegistro, int populacao, int codigoMunicipio, double confirmados100k, double taxaMortalidade) {
        this.data = data;
        this.estado = estado;
        this.casos = casos;
        this.codigoMunicipio = codigoMunicipio;
        this.confirmados100k = confirmados100k;
        this.municipio = municipio;
        this.obitos = obitos;
        this.populacao = populacao;
        this.taxaMortalidade = taxaMortalidade;
        this.tipoLocal = tipoLocal;
        this.ultimoRegistro = ultimoRegistro;
    }

    public String getData() {
        return data;
    }

    public String getEstado() {
        return estado;
    }

    public String getMunicipio() {
        return municipio;
    }

    public String getTipoLocal() {
        return tipoLocal;
    }

    public int getCasos() {
        return casos;
    }

    public int getObitos() {
        return obitos;
    }

    public String getUltimoRegistro() {
        return ultimoRegistro;
    }

    public int getPopulacao() {
        return populacao;
    }

    public int getCodigoMunicipio() {
        return codigoMunicipio;
    }

    public double getConfirmados100k() {
        return confirmados100k;
    }

    public double getTaxaMortalidade() {
        return taxaMortalidade;
    }

    @Override
    public String toString(){
        String txt = this.data + " | " + this.estado + " | " + this.municipio + " | " + this.tipoLocal + " | " + this.populacao + " | " + this.casos + " | " + this.confirmados100k + " | " + this.obitos + " | " + this.taxaMortalidade;
        return txt;
    }
}