var states = [];
const FinalStates = document.getElementById('final-states');
const StartState = document.getElementById('start-state');

const DetermineFinalStates = (Finals) => {
    FinalStatesArray = Finals.split(',');
    FinalStatesArrayClean = [];
    for (state of FinalStatesArray) {
        FinalStatesArrayClean.push(state.trim());
    }
    return FinalStatesArrayClean;
} 

FinalStates.addEventListener('change', () => {
    UpdateGraph(FinalStates.value);
});
function UpdateGraph(Finals) {
    const svg_div = $("#graphviz_svg_div");
    let NodesText = "";
    let Doubles = []
    if (typeof Finals == 'string')
        Doubles = DetermineFinalStates(Finals);
    else
        Doubles = Finals;
    for (state of states) {
        if (state[0] != '' && state[2] != '') {
            if (state[1] == "") {
                NodesText += `${state[0]} -> ${state[2]} [ label = "&#1013;" ];`;
            } else {
                NodesText += `${state[0]} -> ${state[2]} [ label = "${state[1]}" ];`;
            }
        }
    }
    let DoublesText = Doubles.join(" ");
    let data = `digraph finite_state_machine {
                rankdir=LR;
                size="8,5"
                node [shape = doublecircle];
                ${DoublesText}
                node [shape = circle];
                ${NodesText}
            }`;
    let svg = Viz(data, "svg");
    svg_div.html(svg);
}

function addEventListeners(){
    document.querySelectorAll("#statesContainer input").forEach((e) => {
        e.classList.add("custom-form");
        e.addEventListener('change', () => {
            UpdateArray();
            UpdateGraph(FinalStates.value);
        });
    });
}

function UpdateHTML(){
    let sc = $("#statesContainer");
    let radioHTML = "";
    sc.html("");
    for (state of states) {
        if (state[4]) {
            radioHTML = `<input type="radio" name="startState" checked/>`;
        } else {
            radioHTML = `<input type="radio" name="startState"/>`;
        }
        sc.append(`<div class="flex-1 transition">
            <input type="text" value="${state[0]}" />    
            <input type="text" value="${state[1]}" />    
            <input type="text" value="${state[2]}" />
            <button class="deleteState"><i class="fa fa-trash"></i></button>
        </div>`);
    }
    addEventListeners();
}
function UpdateArray(){
    states = new Array();
    Doubles = new Array();
    document.querySelectorAll("#statesContainer > div").forEach((e) => {
        let inputs = e.getElementsByTagName("input");
        if (inputs[0].value != "" && inputs[2].value != "")
            if (state[1] == "") {
                state[1] = 'epsilon';
            }
            states.push([ inputs[0].value, inputs[1].value, inputs[2].value ]);
    });
}

document.querySelectorAll("#statesContainer input").forEach((e) => {
    e.classList.add("custom-form");
    e.addEventListener('change', ()=>{
        UpdateArray();
        UpdateGraph(FinalStates.value);
    });
});

document.getElementById("addState").addEventListener("click", ()=>{
    $("#statesContainer").append(`<div class="flex-1 transition">
            <input type="text" placeholder="From State" />    
            <input type="text" placeholder="Label" />    
            <input type="text" placeholder="To State" />
            <button class="deleteState"><i class="fa fa-trash"></i></button>
        </div>`);
    document.querySelectorAll("#statesContainer input").forEach((e) => {
        e.classList.add("custom-form");
        e.addEventListener('change', () => {
            UpdateArray();
            UpdateGraph(FinalStates.value);
        });
    });
    document.querySelectorAll(".deleteState").forEach((e) => {
        e.addEventListener('click', (el) => {
            el.target.parentElement.parentElement.remove();
            UpdateArray();
            UpdateGraph(FinalStates.value);
        });
    });
});

document.querySelectorAll(".deleteState").forEach((e)=>{
    e.addEventListener('click', (el) => {
        el.target.parentElement.parentElement.remove();
        UpdateArray();
        UpdateGraph(FinalStates.value);
    });
});



function trimStateName(name){
    return name.replaceAll("{", "").replaceAll("}", "").replaceAll(" ", "").replaceAll(",", "");
}

$("#converttodfa").click(()=>{
    let StatesOnly = [];
    let AlphabetsOnly = [];
    let finalStatesOnly = FinalStates.value.split(',');
    for(state of states){
        if (state[1] == '') {
            state[1] = 'epsilon';
        }
    }
    for(state of states){
        StatesOnly.push(state[0]);
        StatesOnly.push(state[2]);
        AlphabetsOnly.push(state[1]);
    }
    for (state of FinalStates.value.split(',')) {
        finalStatesOnly.push(state.trim());
    }
    $.ajax({
        url:"http://localhost:5000/nfatodfa",
        type:"POST",
        data : {
            "states": JSON.stringify(StatesOnly),
            "alphabets": JSON.stringify(AlphabetsOnly),
            "finalStates": JSON.stringify(finalStatesOnly),
            "startState": JSON.stringify(StartState.value.trim()),
            "transitions": JSON.stringify(states),
        },
        success: (e)=>{
            data = JSON.parse(e);
            states = new Array();
            finalStatesToDouble = []
            for(fstd of data._FinalStates)
                finalStatesToDouble.push(trimStateName(fstd));
            for (const Aitem of Object.entries(data._Transitions)) {
                for (const Bitem of Object.entries(Aitem[1])) {
                    states.push([ trimStateName(Aitem[0]) , Bitem[0],trimStateName(Bitem[1]) ]);
                }
            }
            UpdateGraph(finalStatesToDouble);
        },
    });
});

$("#minimize").click(() => {
    let StatesOnly = [];
    let AlphabetsOnly = [];
    let finalStatesOnly = [];

    for (state of finalStatesOnly) {
        state = state.trim();
    }
    for (state of states) {
        StatesOnly.push(state[0]);
        StatesOnly.push(state[2]);
        AlphabetsOnly.push(state[1]);
    }

    for (state of FinalStates.value.split(',')) {
        finalStatesOnly.push(state.trim());
    }
    
    $.ajax({
        url: "http://localhost:5000/minimizedfa",
        type: "POST",
        data: {
            "states": JSON.stringify(StatesOnly),
            "alphabets": JSON.stringify(AlphabetsOnly),
            "finalStates": JSON.stringify(finalStatesOnly),
            "startState": JSON.stringify(StartState.value.trim()),
            "transitions": JSON.stringify(states),
        },
        success: (e) => {
            data = JSON.parse(e);
            states = new Array();
            finalStatesToDouble = []
            for (fstd of data._FinalStates)
                finalStatesToDouble.push(trimStateName(fstd));
            for (const Aitem of Object.entries(data._Transitions)) {
                for (const Bitem of Object.entries(Aitem[1])) {
                    states.push([ trimStateName(Aitem[0]), Bitem[0], trimStateName(Bitem[1]) ]);
                }
            }
            UpdateGraph(finalStatesToDouble);
        },
    });
});

$("#example1").click(() => {
    states = new Array();
    states.push(["a", "0", "b"]);
    states.push(["a", "" , "b"]);
    states.push(["b", "0", "a"]);
    states.push(["b", "1", "b"]);
    states.push(["b", "0", "c"]);
    states.push(["b", "1", "c"]);
    states.push(["c", "1", "c"]);
    UpdateHTML();
    UpdateGraph(['b']);
    document.querySelectorAll(".deleteState").forEach((e)=>{
        e.addEventListener('click', (el) => {
            el.target.parentElement.parentElement.remove();
            UpdateArray();
            UpdateGraph(['b']);
        });
    });
});

$("#example2").click(() => {
    states = new Array();
    states.push(["a", "0", "b"]);
    states.push(["a", "1", "d"]);
    states.push(["b", "0", "e"]);
    states.push(["b", "1", "d"]);
    states.push(["c", "0", "f"]);
    states.push(["c", "1", "b"]);
    states.push(["d", "0", "e"]);
    states.push(["d", "1", "b"]);
    states.push(["e", "0", "f"]);
    states.push(["e", "1", "g"]);
    states.push(["f", "0", "h"]);
    states.push(["f", "1", "g"]);
    states.push(["g", "0", "h"]);
    states.push(["g", "1", "f"]);
    states.push(["h", "0", "d"]);
    states.push(["h", "1", "c"]);
    UpdateHTML();
    UpdateGraph(['a', 'e', 'h']);
    document.querySelectorAll(".deleteState").forEach((e)=>{
        e.addEventListener('click', (el) => {
            el.target.parentElement.parentElement.remove();
            UpdateArray();
            UpdateGraph(['a', 'e', 'h']);
        });
    });
});

$("#example3").click(() => {
    states = new Array();
    states.push(["a", "0", "b"]);
    states.push(["a", "", "b"]);
    states.push(["b", "0", "a"]);
    states.push(["b", "1", "b"]);
    states.push(["c", "0", "b"]);
    states.push(["c", "1", "b"]);
    states.push(["c", "0", "c"]);
    states.push(["b", "1", "c"]);
    states.push(["b", "1", "c"]);
    UpdateHTML();
    UpdateGraph(['b']);
    document.querySelectorAll(".deleteState").forEach((e)=>{
        e.addEventListener('click', (el) => {
            el.target.parentElement.parentElement.remove();
            UpdateArray();
            UpdateGraph(['b']);
        });
    });
});