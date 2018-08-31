const express = require('express')
const app = express()
const bodyParser = require('body-parser')
const cors = require('cors')
const Load = require('./models/load')
const Phase = require('./models/phase')

app.use(bodyParser.urlencoded({ extended: true }))
app.use(bodyParser.json())
app.use(express.static('build'))

var ObjectId = require('mongodb').ObjectID;

const logger = (request, response, next) => {
  console.log('Method:',request.method)
  console.log('Path:  ', request.path)
  console.log('Body:  ', request.body)
  console.log('---')
  next()
}

const formatLoad = (load) => {
  return {
    name: load.name,
    commandBits: load.commandBits,
    maxCurrent: load.maxCurrent,
    phase: load.phase,
    relayPin: load.relayPin,
    priority: load.priority,
    contValue: load.contValue,
    id: load._id
  }
  console.log("Cont value:", load.contValue)
}

const formatPhase = (phase) => {
  return {
    id: phase._id,
    name: phase.name,
    commandBits: phase.commandBits,
    phaseMax: phase.phaseMax,
    maxCurrent: phase.maxCurrent
  }
  console.log("Phase max", phase.phaseMax)
}

let loads = [
  {
    id: 1,
    contValue: 0
  },
  {
    id: 2,
    contValue: 1,
  },
  {
    id: 3,
    contValue: 1,
  }
]

app.get('/', (req, res) => {
  res.send('<h1>Hello World!</h1>')
})

app.use(cors())

app.put('/api/phases/:id', (request, response) => {
  const body = request.body
  const id = request.params.id
  console.log(".......")
  console.log("ID:", id)
  console.log( "Body:", body)
  const phase = {
    phaseMax: body.phaseMax
  }

  Phase
    .findByIdAndUpdate(request.params.id, phase, { new: true } )
    .then(updatedPhase => {
      response.json(formatPhase(updatedPhase))
    })
    .catch(error => {
      console.log(error)
      response.status(400).send({ error: 'malformatted id' })
    })
})


app.put('/api/loads/:id', (request, response) => {
  const body = request.body
  const id = request.params.id
  console.log(".......")
  console.log("ID:", id)
  console.log("Body:", body)
  const load = {
    contValue: body.contValue
  }

  Load
    .findByIdAndUpdate(request.params.id, load, { new: true } )
    .then(updatedLoad => {
      response.json(formatLoad(updatedLoad))
    })
    .catch(error => {
      console.log(error)
      response.status(400).send({ error: 'malformatted id' })
    })
})

app.put('/api/loads/:id/priority', (request, response) => {
  const body = request.body
  const id = request.params.id
  console.log(".......")
  console.log("ID:", id)
  console.log("Body:", body)
  const load = {
    priority: body.priority
  }

  Load
    .findByIdAndUpdate(request.params.id, load, { new: true } )
    .then(updatedLoad => {
      response.json(formatLoad(updatedLoad))
    })
    .catch(error => {
      console.log(error)
      response.status(400).send({ error: 'malformatted id' })
    })
})

app.get('/api/loads', (request, response) => {
  Load
    .find({})
    .then(loads => {
      response.json(loads.map(formatLoad))
    })
})

app.get('/api/phases', (request, response) => {
  Phase
    .find({})
    .then(phases => {
      response.json(phases.map(formatPhase))
    })
})

app.get('/api/loads/:id', (request, response) => {
  Load
    .findById(request.params.id)
    .then(load => {
      response.json(formatLoad(load))
    })
})

app.get('/api/loads/:id/contValue', (request, response) => {
  Load
    .findById(request.params.id)
    .then(load => {
      response.json(formatLoad(load).contValue)
    })
})

app.get('/api/phases/:id/phaseMax', (request, response) => {
  Phase
    .findById(request.params.id)
    .then(phase => {
      response.json(formatPhase(phase).phaseMax)
    })
})


app.post('/api/loads', (request, response) => {
  app.use(logger)
  const body = request.body
  console.log("id:", body._id)
  console.log(body)
  console.log("contValue:", body.contValue)
  if (body.name === undefined) {
    return response.status(400).json({error: 'Value missing, give name, commanBits, maxCurrent, phase, relayPin, priority and contValue '})
  }

  const load = new Load({
    name: body.name,
    commandBits: body.commandBits,
    maxCurrent: body.maxCurrent,
    phase: body.phase,
    relayPin: body.relayPin,
    priority: body.priority,
    contValue: body.contValue,
  })

  load
    .save()
    .then(savedLoad => {
      response.json(formatLoad(savedLoad))
    })
})

app.post('/api/phases', (request, response) => {
  app.use(logger)
  const body = request.body
  console.log("id:", body._id)
  console.log(body)
  console.log("contValue:", body.phaseMax)
  console.log("commandBits:", body.commandBits)

  if (body.commandBits === undefined) {
    return response.status(400).json({error: 'commandBits missing'})
  } if (body.name === undefined) {
      return response.status(400).json({error: 'name missing'})
  } if (body.phaseMax === undefined) {
      return response.status(400).json({error: 'phaseMax missing'})
    }


  const phase = new Phase({
    name: body.name,
    commandBits: body.commandBits,
    phaseMax: body.phaseMax,
    maxCurrent: body.maxCurrent
  })

  phase
    .save()
    .then(savedPhase => {
      response.json(formatPhase(savedPhase))
    })
})

const PORT = process.env.PORT || 3001
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
})
