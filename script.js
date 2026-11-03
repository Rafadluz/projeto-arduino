const IP_RASPBERRY = "192.168.137.154"; 
const URL_API = `http://${IP_RASPBERRY}:8000/leituras`;

const luzElemento = document.getElementById("status-luz");
const statusTexto = document.getElementById("status-texto");
const distanciaTexto = document.getElementById("distancia-texto");
const alarmeSonoro = document.getElementById("audio-alarme");

function consultarVaga() {
    fetch(URL_API)
        .then(response => response.json())
        .then(dados => {
            
            
            if (!dados || dados.distancia === undefined) {
                statusTexto.innerText = "Sem registros ou banco vazio";
                return;
            }

            distanciaTexto.innerText = dados.distancia;

            luzElemento.className = "luz";
            alarmeSonoro.pause();

            switch (dados.status_code) {
                case 0:
                    statusTexto.innerText = "Vaga Livre.";
                    statusTexto.style.color = "#00e676"; 
                    luzElemento.classList.add("verde");
                    break;

                case 1: 
                    statusTexto.innerText = "Manobrando.";
                    statusTexto.style.color = "#ffea00"; 
                    luzElemento.classList.add("piscando-amarelo"); 
                    break;

                case 2:
                    statusTexto.innerText = "Vaga Ocupada.";
                    statusTexto.style.color = "#ff9100"; 
                    luzElemento.classList.add("vermelha-fixa"); 
                    break;

                case 3:
                    statusTexto.innerText = "PERIGO! PARE O VEÍCULO!";
                    statusTexto.style.color = "#ff1744"; 
                    luzElemento.classList.add("piscando-vermelho"); 
                    
                    alarmeSonoro.play().catch(() => {
                        console.log("Clique na tela para habilitar as notificações sonoras.");
                    });
                    break;

                default:
                    statusTexto.innerText = dados.status;
                    luzElemento.classList.add("apagada");
            }
        })
        .catch(error => {
            console.error("Erro ao buscar dados do FastAPI:", error);
            statusTexto.innerText = "Erro de conexão com o servidor da Raspberry";
            statusTexto.style.color = "#ff1744";
            luzElemento.className = "luz apagada";
        });
}

setInterval(consultarVaga, 1000);
