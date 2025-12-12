const submitBtn = document.getElementById('submitBtn');
const origenLon = document.getElementById('origenLon');
const origenLat = document.getElementById('origenLat');
const destinoLon = document.getElementById('destinoLon');
const destinoLat = document.getElementById('destinoLat');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');


submitBtn.addEventListener('click', async () => {
    try {
        if (!isNumeric(origenLon.value)) {
            throw new Error("Debe indicar la longitud del origen en formato numérico.");
        }
        if (!isNumeric(origenLat.value)) {
            throw new Error("Debe indicar la latitud del origen en formato numérico.");
        }
        if (!isNumeric(destinoLon.value)) {
            throw new Error("Debe indicar la longitud del destino en formato numérico.");
        }
        if (!isNumeric(destinoLat.value)) {
            throw new Error("Debe indicar la latitud del destino en formato numérico.");
        }

        hideError();
        submitBtn.textContent = 'Generando';
        submitBtn.disabled = true;

        const queryParams = {
            origen_lon: origenLon.value,
            origen_lat: origenLat.value,
            destino_lon: destinoLon.value,
            destino_lat: destinoLat.value
        };
        
        const queryString = new URLSearchParams(queryParams).toString();
        const response = await fetch(`/api/generar_mapa/?${queryString}`, {
            method: 'GET'
        });

        if (response.ok) {
            const json_response = await response.json();
            openHtmlWindow(json_response)
        } else {
            console.error('Error: ', response.statusText);
            throw new Error("Se produjo un error al generar el mapa.");
        }
    } catch (error) {
        console.error('Error:', error);
        showError(error);
    } finally {
        submitBtn.textContent = 'Generar';
        submitBtn.disabled = false;
    }
});

function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.add('active');
}

function hideError() {
    errorMessage.classList.remove('active');
}

function openHtmlWindow(htmlString) {
    const newWindow = window.open("", "_blank");
    if (newWindow) {
        newWindow.document.write(htmlString);
        newWindow.document.title = 'Mapa de recorrido';
        newWindow.document.close(); 
    } else {
        throw new Error("Pop-up bloqueado. Por favor permita abrir pop-ups para este sitio.");
    }
}

function isNumeric(value) {
    return !isNaN(parseFloat(value)) && isFinite(value);
}
