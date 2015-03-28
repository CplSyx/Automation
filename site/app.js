
/**
 * Module dependencies.
 */

var express = require('express'),
    routes = require('./routes'),  
    socket = require('./routes/socket.js'),
    amqp = require('amqp');




var app = module.exports = express.createServer();
// Hook Socket.io into Express
var io = require('socket.io').listen(app);

//AMQP connection
/* Start listening on the 'updateWeb' queue. This is the only input queue for the web app but it can publish to data and device.*/
function startRabbitMQ() {
	app.rMQconnection = amqp.createConnection({host : 'localhost', port : 5672, login : 'cplsyx', password : 'cplsyx'});
	app.rMQconnection.on('ready', function() {
		//app.exchange = connection.exchange('');
		app.webQueue = app.rMQconnection.queue('updateWeb', {durable : true, autoDelete: false});
		app.webQueue.bind('#'); //# means all messages on the queue
		app.webQueue.subscribe(function (message) {
			/*io.emit('send:message', {
				user: "Rabbit",
				text: message.data.toString('utf8')
			});*/
			//app.rMQconnection.publish('updateDevice', message.data.toString('utf8')); //This works but leaving it here results in a send/receive loop!
			console.log(message.data.toString('utf8'));
		});
	

	});
console.log("...");
}

// Configuration

app.configure(function(){
  app.set('view options', {
    layout: false
  });
  app.use(express.bodyParser());
  app.use(express.methodOverride());
  app.use(express.static(__dirname + '/public'));
  app.use(app.router);
});

app.configure('development', function(){
  app.use(express.errorHandler({ dumpExceptions: true, showStack: true }));
});

app.configure('production', function(){
  app.use(express.errorHandler());
});

// Start server

app.listen(3000, function(){
  console.log("Express server listening on port %d in %s mode", app.address().port, app.settings.env);
});
startRabbitMQ();

// Socket.io Communication
io.sockets.on('connection', function (socket) {
  // broadcast a command to other apps
  socket.on('send:command', function (data) {
    socket.broadcast.emit('send:command', {
      command: data.command
    });
    app.rMQconnection.publish('updateDevice', "{sender:web, message:"+data.command.toString('utf8')+"}");
    console.log("{\"sender\":\"web\", \"message\":\""+data.command.toString('utf8')+"\"}");
  });

});

