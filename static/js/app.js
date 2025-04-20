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
        // .then(res => res.text())
        // .then(res => {console.log(typeof(res)), console.log(res.text())})
        .then(res => res.text())
        .then(
            res => {
                x = (res)
                x = JSON.parse(res)
                console.log(x)
                chartDiv = document.getElementById('chart')
                chartDiv.innerHTML = x['plot'];

                $.each(x['month_year'], function (i, value) {
                    $('#period').append($('<option></option>').val(value).text(value));
                    const selectElement = document.getElementById('period');
                    selectElement.selectedIndex = selectElement.options.length - 1;
                });

                const scripts = chartDiv.querySelectorAll('script');
                if (scripts) {
                    scripts.forEach((e) => {
                        eval(e.textContent);
                    })
                }
            }
        )
        .catch(console.error);
};

const select = document.getElementById('period');
select.addEventListener('change', () => {
    goToPeriod()
});

document.getElementById('prevPeriod').addEventListener('click', () => {
    if (select.selectedIndex > 0) {
        select.selectedIndex -= 1;
        goToPeriod()
    }
});

document.getElementById('nextPeriod').addEventListener('click', () => {
    if (select.selectedIndex < select.options.length - 1) {
        select.selectedIndex += 1;
        goToPeriod()
    }
});

function goToPeriod() {
    fetch(`${window.location.origin}/queryPeriod?period=${select.value}`, {
        method: 'GET'
    })
        .then(res => res.text())
        .then(
            res => {
                x = JSON.parse(res)
                chartDiv = document.getElementById('chart')
                chartDiv.innerHTML = x['plot'];
                const scripts = chartDiv.querySelectorAll('script');
                if (scripts) {
                    scripts.forEach((e) => {
                        eval(e.textContent);
                    })
                }
            }
        )
        .catch(console.error);
}

function changeColorScheme() {
    const colors = [];
    const colorSelectors = document.querySelectorAll(`.colorSelector`)
    colorSelectors.forEach((e) => {
        colors.push(e.value);
    })
    console.log(colors)

    fetch(`${window.location.origin}/color`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            colors: colors
        })
    })
        .then(res => res.text())
        .then(
            res => {

            }
        )
        .catch(console.error);
}