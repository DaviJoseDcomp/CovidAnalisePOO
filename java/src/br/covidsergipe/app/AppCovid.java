package br.covidsergipe.app;

import br.covidsergipe.ui.*;
import javax.swing.SwingUtilities;

public class AppCovid {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new AnaliseCovidGUI().setVisible(true);
        });
    }
}
