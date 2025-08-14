package br.covidsergipe.model;

public class RegistroCovid {

    private String data;
    private String municipio;
    private int casosNovos;
    private int obitosNovos;
    private int vacinadosNovos;
    private int casosAcumulados;
    private int obitosAcumulados;
    private int vacinadosAcumulados;

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







}