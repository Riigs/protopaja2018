import React from 'react'
import Visual from './Visual.js'

const Navbar= () => {
  return(
    <nav class="navbar navbar-inverse">
      <div class="container-fluid">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#myNavbar">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="#">Kuormanohjausyksikkö</a>
        </div>
        <div class="collapse navbar-collapse" id="myNavbar">
          <ul class="nav navbar-nav">
            <li class="active"><a href="#">Home</a></li>
            <li class="dropdown">
              <a class="dropdown-toggle" data-toggle="dropdown" href="#">Visual
              <span class="caret"></span></a>
              <Visual />
            </li>
            <li><a href="cat2">Phases</a></li>
            <li><a href="cat3">Loads</a></li>
          </ul>
          <ul class="nav navbar-nav navbar-right">
          </ul>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
