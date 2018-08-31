import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import axios from 'axios'
import Load from './components/Load.js'
import Graph from './components/Graph.js'
import Phase from './components/Phase.js'

  class App extends React.Component {
    constructor(props) {
      super(props)
      this.state = {
        loads : [],
        phases : [{maxPhase:0}],
        newVal: '',
        showAll: true,
        newPhaseMax: '',
        newPriority:'',
        }
      console.log('constructor')
    }

    changeContValue = (id, val) => {
    return () => {
    const url = `https://salty-mountain-85076.herokuapp.com/api/loads/${id}`
    const load = this.state.loads.find(n => n.id === id)
    const changedLoad = { ...load, contValue: val }
    console.log("URL:", url)

    axios
      .put(url, changedLoad)
      .then(response => {
        this.setState({
          loads: this.state.loads.map(load => load.id !== id ? load : response.data)
        })
      })
    }
  }

  handlePhaseMaxChange = (event) => {
    console.log("Phase handler:", event.target.value)
    this.setState({newPhaseMax: event.target.value})
}

  changePhaseMax = (event) => {
    event.preventDefault()
    const id = '5b6c22aab08216000447b9fc'
    const phase = this.state.phases.find(n => n.id === id)
    const url = `https://salty-mountain-85076.herokuapp.com/api/phases/${id}`
    const changedPhaseMax = {...phase, phaseMax:this.state.newPhaseMax }
    this.setState({
      phases: this.state.phases.map(phase => phase.id !== id ? phase : changedPhaseMax)
    })

    axios
        .put(url, changedPhaseMax)
        .then(response => {
          this.setState({
            phases: this.state.phases.map(phase => phase.id !== id ? phase : response.data)
          })
          console.log("Response data:", response.data)
          }
          )
    }

    componentDidMount() {
      console.log('did mount')
      axios
        .get('https://salty-mountain-85076.herokuapp.com/api/loads')
        .then(response => {
          console.log('promise fulfilled')
          this.setState({ loads: response.data })
        })
      axios
        .get('https://salty-mountain-85076.herokuapp.com/api/phases')
        .then(response => {
          console.log('promise fulfilled')
          this.setState({ phases: response.data })
        })
    }

    asetaArvoon(o, arvo) {
      return () => {
        this.setState({ [o] : [arvo]}
        )
      }
    }

  turnOn = (event) => {
      this.setState({ notes: 1 })
      console.log('ok toggle')
    }

  addLoad = (event) => {
  event.preventDefault()
  const loadObject = {
    contValue: this.state.contValue,
    name: this.state.name,
    priority: 'x'
  }


  axios.post('https://salty-mountain-85076.herokuapp.com/api/loads', loadObject)
    .then(response => {
      console.log(response)
    })
  }

  changePriority = (event, id) => {
    console.log("Priority ok", id)
    event.preventDefault()
    const load = this.state.loads.find(n => n.id === id)
    const url = `https://salty-mountain-85076.herokuapp.com/api/loads/${id}/priority`
    console.log("URL:", url)
    const changedPriority = {...load, priority:this.state.newPriority }
    this.setState({
      loads: this.state.loads.map(load => load.id !== id ? load : changedPriority)
    })

    axios
        .put(url, changedPriority)
        .then(response => {
          this.setState({
            loads: this.state.loads.map(load => load.id !== id ? load : response.data)
          })
          console.log("Response data:", response.data)
          }
          )
    }

  handlePriorityChange = (event) => {
    console.log("Handle priority change:", event.target.value)
    this.setState({newPriority: event.target.value})
  }

funktio = (event) => {
console.log('ok')
const loadObject = {
  content: this.state.newVal,
  value: this.state
}

axios.post('https://salty-mountain-85076.herokuapp.com/api/loads', loadObject)
  .then(response => {
    console.log(response)
  })
}

    render() {
      return (
        <div>
        <nav className="navbar navbar-inverse">
          <div className="container-fluid">
            <div className="navbar-header">
              <button type="button" className="navbar-toggle" data-toggle="collapse" data-target="#myNavbar">
                <span className="icon-bar"></span>
                <span className="icon-bar"></span>
                <span className="icon-bar"></span>
              </button>
              <a className="navbar-brand" href="#">Kuormanohjausyksikkö</a>
            </div>
            <div className="collapse navbar-collapse" id="myNavbar">
              <ul className="nav navbar-nav">
                <li className="active"><a href="cat1">Kulutus</a></li>
                <li><a href="#cat2">Vaiheet</a></li>
                <li><a href="#cat3">Kuormat</a></li>
              </ul>
              <ul className="nav navbar-nav navbar-right">
              </ul>
            </div>
          </div>
        </nav>
        <div id="cat1">
          <Graph />
        </div>


        <div id="cat2">
          <div className="page-header">
            <h2>Vaiheet</h2>
          </div>
          <p>Maksimituntiteho: {this.state.phases[0].phaseMax} Wh</p>
          {console.log(this.state.phases[0].phaseMax)}
          <form onSubmit={this.changePhaseMax}>
          Muuta maksimituntiteho: <input value={this.state.newPhaseMax} placeholder={this.state.phases[0].phaseMax} onChange={this.handlePhaseMaxChange}/>
          <button type="submit">Tallenna</button>
          </form>
            <ul>
              {this.state.phases.map(phase => <Phase key={phase.name} phase={phase} this={this}/>)}
            </ul>
        </div>

        <div id="cat3">
          <div className="page-header">
            <h2>Kuormat</h2>
          </div>
            <ul>
              {this.state.loads.map(load => <Load key={load.id} id={load.id} name={load.name} this={this} contValue={load.contValue} priority={load.priority} />)}
            </ul>
        </div>
            {console.log('render')}
            {console.log("Loads:", this.state.loads)}
        </div>
      )
    }
  }



ReactDOM.render(<App />, document.getElementById('root'))
