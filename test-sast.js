// Teste intencional para SAST
function processarInput(userInput) {
    // VULNERABILIDADE: uso de eval()
    eval(userInput);
}

processarInput("console.log('Olá!')");
