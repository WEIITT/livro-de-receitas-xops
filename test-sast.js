// Teste SAST - vulnerabilidade intencional
const dados = "teste";
eval("console.log('SAST a funcionar: ' + dados)");
