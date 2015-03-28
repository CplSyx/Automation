// export function for listening to the socket
module.exports = function (socket) {
/*
  // broadcast a user's message to other users
  socket.on('send:message', function (data) {
    socket.broadcast.emit('send:message', {
      user: name,
      text: data.message
    });
  });
*/  
  // broadcast a command to other apps
  socket.on('send:command', function (data) {
    socket.broadcast.emit('send:command', {
      command: data.command
    });
    //app.rMQconnection.publish('updateDevice', data.command);
    console.log(data.command);
  });

};
