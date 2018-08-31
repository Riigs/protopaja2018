const mongoose = require('mongoose')

const url = 'mongodb://proto:tyypp1@ds111390.mlab.com:11390/loads'

mongoose.connect(url)

const Phase = mongoose.model('Phase', {
  name: String,
  commandBits: String,
  phaseMax: String,
  maxCurrent: String
})

module.exports = Phase
