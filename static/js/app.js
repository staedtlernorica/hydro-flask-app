const moreText = document.getElementById("moreText");
const preview = document.getElementById("preview");
const btn = document.querySelector(".toggle-btn");

function toggleText() {
    moreText.classList.toggle("hide");
    preview.classList.toggle("collapsed");

    const isHidden = moreText.classList.contains("hide");
    btn.textContent = isHidden ? "See More" : "See Less";
}

xmlFile = document.querySelector('#xmlFile')
xmlSampleFile = '../../sample xml/output.xml'

function handleUploadClick(btnType) {
    let uploadUrl = `${window.location.origin}/upload?dataSrc=sample`;  //default to use sample data 
    let formData
    if (btnType === 'submit') {
        const file = xmlFile.files[0];
        uploadUrl = `${window.location.origin}/upload?dataSrc=submit`;
        formData = new FormData();
        formData.append('file', file); // 'file' is the expected field name
    }

    fetch(uploadUrl, {
        method: 'POST',
        body: formData
    })
        .then(res => res.text())
        .then(res => {
            let parsed = JSON.parse(res);
            const chartDiv = document.getElementById('chart');
            chartDiv.className = ''
            chartDiv.innerHTML = parsed['plot'];
            const periodSelect = document.getElementById('period');
            periodSelect.innerHTML = ''; // clear previous options if any

            parsed['month_year'].forEach(value => {
                const option = document.createElement('option');
                option.value = value;
                option.textContent = value;
                periodSelect.appendChild(option);
            });

            periodSelect.selectedIndex = periodSelect.options.length - 1;

            const scripts = chartDiv.querySelectorAll('script');
            scripts.forEach(script => eval(script.textContent));
        })
        .catch(console.error);
}

submitBtn = document.querySelector('#submitXml')
sampleBtn = document.querySelector('#sampleXml')
submitBtn.onclick = () => handleUploadClick('submit');
sampleBtn.onclick = () => handleUploadClick('sample');


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