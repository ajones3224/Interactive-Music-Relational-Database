let questions = null;
let current_pos = 0;
let current_q = null;
let correct = null;
let amt_correct = 0;
let start = Date.now();
let choiceMade = false;


// Initialization functions
function init(qs) {
    questions = qs;
    current_q = questions[0];
}

function setText() {
    let q_elements = current_q.split('|');
    document.getElementById('question').innerHTML = q_elements[0];
    document.getElementById('a').innerHTML = q_elements[1];
    document.getElementById('b').innerHTML = q_elements[2];
    document.getElementById('c').innerHTML = q_elements[3];
    document.getElementById('d').innerHTML = q_elements[4];
    correct = q_elements[5];
}

window.onload = function() {
    document.getElementById('btn_home').onclick = function() {
        location.href = '/billbored/';
    }
    setText();
}


// Timer functions
function formatNum(n) {
    return n > 9 ? "" + n : "0" + n;
}

function setTimer() {
    let timeElapsed = Date.now() - start;
    let seconds = formatNum(Math.floor((timeElapsed / 1000) % 60));
    let minutes = formatNum(Math.floor((timeElapsed / 1000 / 60) % 60));
    document.getElementById('timer').innerHTML = minutes + ':' + seconds;
    setTimeout(setTimer, 1000);
}
setTimeout(setTimer, 1000);


//Question functions
function changeQ() {
    let btns = document.getElementsByTagName('button');
    for (let i = 0; i < btns.length; i++) {
        btns[i].style.backgroundColor = 'rgba(230, 241, 252, 1)';
        btns[i].style.color = 'rgba(25, 137, 250, 1)';
        btns[i].disabled = false;
    }
    
    if (current_pos+1 >= questions.length) {
        localStorage.setItem('amt_correct', amt_correct);
        localStorage.setItem('time', document.getElementById('timer').innerHTML);
        location.href = 'end_page.html';
    } else {
        current_pos++;
        current_q = questions[current_pos];
        setText();
        choiceMade = false;
    }
}


// Choice display functions
function disableButton(btns) {
    for (let i = 0; i < btns.length; i++) {
        if (btns[i].id != correct) {
            document.getElementById(btns[i].id).style.backgroundColor = 'rgba(200, 211, 232, 1)';
            document.getElementById(btns[i].id).disabled = true;
        }
    }
}

function changeChoiceColor(id) {
    let allBtns = document.getElementsByClassName('btn_choice');
    disableButton(allBtns)
    if (id == correct) {
        document.getElementById(id).style.backgroundColor = 'rgba(179, 222, 193, 1)';
        amt_correct++;
    } else {
        document.getElementById(id).style.color = 'rgba(255, 255, 255, 1)';
        document.getElementById(id).style.backgroundColor = '#e17477';
        document.getElementById(correct).style.backgroundColor = 'rgba(179, 222, 193, 1)';
    }
    choiceMade = true;
    setTimeout(changeQ, 1000);
}

function hoverColor(id) {
    document.getElementById(id).style.backgroundColor = 'rgba(200, 211, 232, 1)';
}

function removeHoverColor(id) {
    if (!choiceMade) {
        document.getElementById(id).style.backgroundColor = 'rgba(230, 241, 252, 1)';
    }
}
