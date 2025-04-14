submitBtn = document.querySelector('#submitXml')
xmlFile = document.querySelector('#xmlFile')

submitBtn.onclick = () => {
    const file = xmlFile.files[0];
    const formData = new FormData();
    formData.append('file', file); // 'file' is the field name expected by the backend

    fetch(`${window.location.origin}/upload`, {
            method: 'POST',
            body: formData
        })
        .then(res => res.text())
        .then(  
            res => {
                chartDiv = document.getElementById('chart')
                chartDiv.innerHTML = res;
                const scripts = chartDiv.querySelectorAll('script');
                scripts.forEach((e) => {
                    eval(e.textContent); // 👈 executes the Plotly.newPlot(...) code
                })
            }
        )
        .catch(console.error);
};