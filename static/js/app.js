const LOADING_ANIMATION = false
const CHART = document.getElementById("chart")
const LOADER = document.getElementById("loaderContainer")
LOADER.style.display = 'none'

function loadingAnimation(loading){
    if (loading){
        LOADER.style.display = 'flex'
        CHART.style.opacity = '15%'
        return
    }
    LOADER.style.display = 'none'
    CHART.style.opacity = '100%'
}

const moreText = document.getElementById("moreText");
const preview = document.getElementById("preview");
const btn = document.querySelector(".toggleBtn");

function toggleText() {
    moreText.classList.toggle("hide");
    preview.classList.toggle("collapsed");

    const isHidden = moreText.classList.contains("hide");
    btn.textContent = isHidden ? "See More" : "See Less";
}

xmlFile = document.querySelector('#xmlFile')
xmlSampleFile = '../../sample xml/output.xml'

function handleUploadClick(btnType) {
    loadingAnimation(true)
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
        .then(
            res => {
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
                loadingAnimation(false)
            })
        .catch(console.error);
}

submitBtn = document.querySelector('#submitXml')
sampleBtn = document.querySelector('#sampleXml')
submitBtn.onclick = () => handleUploadClick('submit');
sampleBtn.onclick = () => handleUploadClick('sample');


const TIME_PERIOD_SELECT = document.getElementById('period');
TIME_PERIOD_SELECT.addEventListener('change', () => {
    goToPeriod()
});

document.getElementById('prevPeriod').addEventListener('click', () => {
    if (TIME_PERIOD_SELECT.selectedIndex > 0) {
        TIME_PERIOD_SELECT.selectedIndex -= 1;
        goToPeriod()
    }
});

document.getElementById('nextPeriod').addEventListener('click', () => {
    if (TIME_PERIOD_SELECT.selectedIndex < TIME_PERIOD_SELECT.options.length - 1) {
        TIME_PERIOD_SELECT.selectedIndex += 1;
        goToPeriod()
    }
});

function goToPeriod() {
    loadingAnimation(true)
    fetch(`${window.location.origin}/queryPeriod?period=${TIME_PERIOD_SELECT.value}`, {
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
                loadingAnimation(false)
            }
        )
        .catch(console.error);
}

function changeColorScheme() {
    let colors = [];
    const colorSelectors = document.querySelectorAll(`.colorSelector`)
    colorSelectors.forEach((e) => {
        colors.push(e.value);
    })
    colors = colors.join('|')
    
    // send in 'empty' so /color function only set custom color cookies
    // and doesn't query time period/create chart, saving rendering time
    periodIsEmpty = TIME_PERIOD_SELECT.value === ''
    period = TIME_PERIOD_SELECT.value

    loadingAnimation(true)
    fetch(`${window.location.origin}/color`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            colors: colors,
            currentPeriod: periodIsEmpty ? 'empty' : period
        })
    })
        .then(res => res.text())
        .then(
            res => {
                if (!periodIsEmpty){
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
                loadingAnimation(false)
            }
        )
        .catch(console.error);
}

function resetColorScheme(){

}