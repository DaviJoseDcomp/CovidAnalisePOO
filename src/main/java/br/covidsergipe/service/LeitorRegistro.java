package br.covidsergipe.service;

import br.covidsergipe.model.*;
import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class LeitorRegistro {
    
    public static List<RegistroCovid> lerArquivo(String caminho) {
        List<RegistroCovid> registros = new ArrayList<>();

        try(Scanner scanner = new Scanner(new File(caminho))) {
            if(scanner.hasNextLine()){
                scanner.nextLine();
            }

            while(scanner.hasNextLine()){
                String linha = scanner.nextLine();
                String[] campos = linha.split(";");
                String data = campos[0];
                String estado = campos[1];
                String municipio = campos[2];
                String tipoLocal = campos[3];
                int casos = Integer.parseInt(campos[4]);
                int obitos = Integer.parseInt(campos[5]);
                String ultimoRegistro = campos[6];
                int populacao = Integer.parseInt(campos[7]);
                int codigoMunicipio = Integer.parseInt(campos[8]);
                double confirmados100k = Double.parseDouble(campos[9].replace(",", "."));
                double taxaMortalidade = Double.parseDouble(campos[10].replace(",", "."));

                RegistroCovid registro = new RegistroCovid(data, estado, municipio, tipoLocal, casos, obitos, ultimoRegistro, populacao, codigoMunicipio, confirmados100k, taxaMortalidade);
                registros.add(registro);

            }

        } catch(Exception e){
            System.out.println("Erro ao ler arquivo: " + e.getMessage());
        }

        
        return registros;
    }
}
