import React from 'react'

const Phase = (props) => {
  const p = props.phase
  return(
    <div>
      <h3>{p.name}</h3>
      <p>ID: {p.id} </p>
      <p>Maksimivirta: {p.maxCurrent} A</p>
    </div>
  )
}

export default Phase
