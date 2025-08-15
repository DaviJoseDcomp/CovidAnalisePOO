package br.covidsergipe.model;

public class RegistroCovid {

    private final String data;
    private final String municipio;
    private final int casosNovos;
    private final int obitosNovos;
    private final int vacinadosNovos;
    private final int casosAcumulados;
    private final int obitosAcumulados;
    private final int vacinadosAcumulados;

    public RegistroCovid(String data, String municipio, int casosNovos, int obitosNovos, int vacinadosNovos, int casosAcumulados, int obitosAcumulados, int vacinadosAcumulados){
        
        this.data = data;
        this.municipio = municipio;
        this.casosNovos = casosNovos;
        this.obitosNovos = obitosNovos;
        this.vacinadosNovos = vacinadosNovos;
        this.casosAcumulados = casosAcumulados;
        this.obitosAcumulados = obitosAcumulados;
        this.vacinadosAcumulados = vacinadosAcumulados;
        
}

    public String getData() {
        return data;
    }

    public String getMunicipio() {
        return municipio;
    }

    public int getCasosNovos() {
        return casosNovos;
    }

    public int getObitosNovos() {
        return obitosNovos;
    }

    public int getVacinadosNovos() {
        return vacinadosNovos;
    }

    public int getCasosAcumulados() {
        return casosAcumulados;
    }

    public int getObitosAcumulados() {
        return obitosAcumulados;
    }

    public int getVacinadosAcumulados() {
        return vacinadosAcumulados;
    }

}