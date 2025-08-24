package br.covidsergipe.service;

import br.covidsergipe.model.RegistroCovid;
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
                RegistroCovid registro = new RegistroCovid(campos[0], campos[1], campos[2], campos[3], Integer.parseInt(campos[4]), Integer.parseInt(campos[5]), campos[6], Integer.parseInt(campos[7]), Integer.parseInt(campos[8]), Double.parseDouble(campos[9]), Double.parseDouble(campos[10]));
                registros.add(registro);

            }

        } catch(Exception e){
            System.out.println("Erro ao ler arquivo: " + e.getMessage());
        }

        
        return registros;
    }
}
