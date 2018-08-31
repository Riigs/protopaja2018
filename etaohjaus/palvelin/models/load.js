const mongoose = require('mongoose')

const url = 'mongodb://proto:tyypp1@ds111390.mlab.com:11390/loads'

mongoose.connect(url)

const Load = mongoose.model('Load', {
  name: String,
  commandBits: String,
  maxCurrent: String,
  phase: String,
  relayPin: String,
  priority: String,
  contValue: String,
})

module.exports = Load
