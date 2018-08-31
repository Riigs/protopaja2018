const mongoose = require('mongoose')

// korvaa url oman tietokantasi urlilla. ethän laita salasanaa Githubiin!
const url = ''
var ObjectId = require('mongodb').ObjectID;

mongoose.connect(url)

const Load = mongoose.model('Load', {
  contValue: String,
})

const load = new Load({
  contValue: '1',
})

load
  .save()
  .then(response => {
    console.log('load saved!')
    mongoose.connection.close()
  })
