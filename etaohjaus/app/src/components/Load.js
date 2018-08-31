import React from 'react'

const Load = (props) => {
  const load = props.name
  const id = props.id
  console.log("Loads:", props.name)
  console.log("Load debug:", id)
  console.log("Props in load:", props)
  console.log("Props.load:", load, props.name)

function state() {
  console.log('ContValue:', props.contValue)
    if (props.contValue==='0'){
      return(
        <div className="label label-success">Päällä</div>
      )
    } if (props.contValue==='1'){
      return(
        <div className="label label-danger">Pois</div>
      )
    } else {
      return('None')
    }
  }

function priority() {
  console.log("Priority:", props.priority)
  return (
    <div className="label label-default">{props.priority}</div>
  )
}


  return(
    <div>
      <li className="list-group-item">
      <div className="panel panel-default">
        <div className="panel-heading">
          <h4 className="panel-title">
            <a data-toggle="collapse" href={"#"+String(id)}>{props.name} | {state()} | {priority()}</a>
          </h4>
        </div>
        <div id={String(id)} className="panel-collapse collapse">
          <ul className="list-group">
            <ul>ID: {id} </ul>
            <ul> <button onClick={props.this.changeContValue(id, 0)} className="btn-success">
                  päälle
                  </button>
                  <button onClick={props.this.changeContValue(id, 1)} className="btn-danger">
                  pois
                  </button>
            </ul>
            <ul>
              <form onSubmit={(e) => props.this.changePriority(e, props.id)}>
              Prioriteetti: <input value={props.this.state.newPriority} placeholder={props.priority} onChange={props.this.handlePriorityChange}/>
              <button type="submit">Tallenna</button>
              </form>
            </ul>
          </ul>
        </div>
      </div>
      </li>
    </div>
  )
}

export default Load
