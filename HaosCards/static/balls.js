const { Engine, Render, Runner, Bodies, Body, Composite, Events } = Matter;

const engine = Engine.create();
const canvasContainer = document.getElementById('canvas-container');

const render = Render.create({
  element: canvasContainer,
  engine: engine,
  options: {
    width: 600,
    height: 600,
    wireframes: false,
  }
});

const nameLabels = ['John', 'Mike', 'Anna', 'Bob', 'Carol', 'Daniel', 'Ethan'];

const balls = nameLabels.map((name, index) => {
  const ball = Bodies.circle(
    Math.random() * render.options.width,
    Math.random() * render.options.height,
    50,
    { restitution: 1, friction: 0.02, frictionAir: 0.02 }
  );
  ball.label = name;
  return ball;
});


Composite.add(engine.world, balls);

// Add walls
const borderThickness = 10; // Adjust as needed
const borders = [
  Bodies.rectangle(render.options.width / 2, 0 - borderThickness / 2, render.options.width, borderThickness, { isStatic: true}),
  Bodies.rectangle(render.options.width / 2, render.options.height + borderThickness / 2, render.options.width, borderThickness, { isStatic: true}),
  Bodies.rectangle(0 - borderThickness / 2, render.options.height / 2, borderThickness, render.options.height, { isStatic: true}),
  Bodies.rectangle(render.options.width + borderThickness / 2, render.options.height / 2, borderThickness, render.options.height, { isStatic: true})
];

Composite.add(engine.world, borders);

Runner.run(engine);
Render.run(render);

Events.on(engine, 'afterUpdate', function() {
  const context = render.context;
  balls.forEach((ball) => {
    context.font = '20px Arial';
    context.fillStyle = 'black'; // Set font color
    context.fillText(ball.label, ball.position.x, ball.position.y);
  });
});

balls.forEach(ball => {
  Body.setVelocity(ball, { x: (Math.random() - 0.5) * 10, y: (Math.random() - 0.5) * 10 });
});