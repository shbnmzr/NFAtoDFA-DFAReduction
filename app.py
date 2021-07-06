from FiniteAutomata.Nfa import Nfa
from FiniteAutomata.Dfa import Dfa
from flask import Flask, render_template
import os
import sys
import json
import copy
from flask import request
from flask_cors import CORS


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


app = Flask(__name__)
CORS(app)


@app.route("/")
def hello_world():
    return render_template('index.html')


@app.route("/minimizedfa", methods=["POST"])
def Minimize():
    States = set(json.loads(request.form.get('states')))
    Alphabets = set(json.loads(request.form.get('alphabets')))
    Data = json.loads(request.form.get('transitions'))
    Transitions = dict()

    for i, State in enumerate(Data):
        if State[0] not in Transitions:
            Transitions[State[0]] = dict({State[1]: [State[2]]})
        else:
            if State[1] not in Transitions[State[0]]:
                Transitions[State[0]][State[1]] = [State[2]]
            else:
                Transitions[State[0]][State[1]].append(State[2])
    for State in Transitions:
        for Alphabet in Alphabets:
            if not Alphabet in Transitions[State]:
                Transitions[State][Alphabet] = []
    StartState = str(json.loads(request.form.get('startState')))
    FinalStates = set(json.loads(request.form.get('finalStates')))
    DfaMachinine = Dfa(States, Alphabets, Transitions, StartState, FinalStates)
    MinimizedDfa = DfaMachinine.MinimizeDfa()
    for State in MinimizedDfa._Transitions:
        if MinimizedDfa._Transitions[State] == {}:
            MinimizedDfa._Transitions.pop(State)
        for Alphabet in MinimizedDfa._Alphabets:
            if MinimizedDfa._Transitions[State][Alphabet] == '':
                MinimizedDfa._Transitions[State].pop(Alphabet)
    return json.dumps(MinimizedDfa.__dict__, default=set_default)


@app.route("/nfatodfa", methods=["POST"])
def NFAToDFA():
    StatesNfa = set(json.loads(request.form.get('states')))
    AlphabetsNfa = set(json.loads(request.form.get('alphabets')))
    for Alphabet in AlphabetsNfa:
        if Alphabet == 'epsilon':
            AlphabetsNfa.add(Nfa.EPSILON)
            AlphabetsNfa.remove('epsilon')
    Data = json.loads(request.form.get('transitions'))
    for Transition in Data:
        if Transition[1] == 'epsilon':
            Transition[1] = Nfa.EPSILON
    Transitions = dict()
    for i, State in enumerate(Data):
        if State[0] not in Transitions:
            Transitions[State[0]] = dict({State[1]: [State[2]]})
        else:
            if State[1] not in Transitions[State[0]]:
                Transitions[State[0]][State[1]] = [State[2]]
            else:
                Transitions[State[0]][State[1]].append(State[2])
    for State in StatesNfa:
        if State in Transitions:
            for Alphabet in AlphabetsNfa:
                if not Alphabet == Nfa.EPSILON:
                    if not Alphabet in Transitions[State]:
                        Transitions[State][Alphabet] = []
        else:
            Transitions[State] = dict()
            for Alphabet in AlphabetsNfa:
                if not Alphabet == Nfa.EPSILON:
                    Transitions[State][Alphabet] = []
    TransitionsNfa = Transitions
    StartStateNfa = str(json.loads(request.form.get('startState')))
    FinalStatesNfa = set(json.loads(request.form.get('finalStates')))
    NfaMachine = Nfa(StatesNfa, AlphabetsNfa, TransitionsNfa,
                     StartStateNfa, FinalStatesNfa)
    EqDfa = NfaMachine.ToDfa()
    NewEq = copy.deepcopy(EqDfa._Transitions)
    for State in EqDfa._Transitions:
        if EqDfa._Transitions[State] == {}:
            NewEq.pop(State)
            continue
    EqDfa._Transitions = copy.deepcopy(NewEq)
    return json.dumps(EqDfa.__dict__, default=set_default)
