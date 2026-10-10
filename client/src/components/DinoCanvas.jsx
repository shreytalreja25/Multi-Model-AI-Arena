import React, { useRef, useEffect } from 'react';

/**
 * 60 FPS Cyberpunk Chrome Dinosaur Runner Canvas Component
 * Renders animated cyber-dino, scrolling neon grid, cacti barriers,
 * flying drones/pterodactyls, and real-time hazard trajectory HUD.
 */
export default function DinoCanvas({
  gameState,
  lastEvent,
  modelColor = '#00f3ff',
  isAlive = true,
  width = 300,
  height = 190,
}) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId;

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // 1. Cyberpunk Dark Horizon Gradient
      const grad = ctx.createLinearGradient(0, 0, 0, height);
      grad.addColorStop(0, '#05070d');
      grad.addColorStop(0.65, '#0b1120');
      grad.addColorStop(1, '#050811');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, width, height);

      const groundY = height - 38;
      const speed = gameState?.speed || 6.0;
      const tick = gameState?.tick || 0;
      const dist = gameState?.distance || 0;
      const dinoData = gameState?.dino || {};
      const dinoY = dinoData.y || 0;
      const isJumping = dinoData.is_jumping || dinoY > 0;
      const isDucking = dinoData.is_ducking || false;

      // 2. Scrolling Cyber Grid Ground
      ctx.save();
      ctx.strokeStyle = 'rgba(0, 243, 255, 0.4)';
      ctx.lineWidth = 1.5;
      ctx.shadowColor = '#00f3ff';
      ctx.shadowBlur = 6;
      ctx.beginPath();
      ctx.moveTo(0, groundY);
      ctx.lineTo(width, groundY);
      ctx.stroke();
      ctx.restore();

      // Perspective floor lines
      ctx.save();
      ctx.strokeStyle = 'rgba(0, 243, 255, 0.12)';
      ctx.lineWidth = 1;
      const gridOffset = (tick * speed * 1.5) % 24;
      for (let x = -gridOffset; x < width + 24; x += 24) {
        ctx.beginPath();
        ctx.moveTo(x, groundY);
        ctx.lineTo(x - 16, height);
        ctx.stroke();
      }
      ctx.restore();

      // 3. Render Obstacles
      const obstacles = gameState?.obstacles || [];
      obstacles.forEach(obs => {
        // Map engine X (0-680) to canvas width ratio
        const scaleX = width / 400.0;
        const ox = (obs.x - 20) * scaleX;
        const ow = Math.max(12, obs.width * scaleX);
        const oh = obs.height * 1.0;
        const oy = groundY - obs.y - oh;

        if (ox > -50 && ox < width + 50) {
          ctx.save();
          if (obs.type.includes('ptero')) {
            // Flying Pterodactyl / Cyber-Drone
            const wingFlap = Math.sin(tick * 0.45) * 8;
            ctx.fillStyle = '#c084fc';
            ctx.strokeStyle = '#e879f9';
            ctx.lineWidth = 1.5;
            ctx.shadowColor = '#e879f9';
            ctx.shadowBlur = 8;

            // Fuselage
            ctx.beginPath();
            ctx.ellipse(ox + ow / 2, oy + oh / 2, ow / 2, 6, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();

            // Cyber-Wings
            ctx.beginPath();
            ctx.moveTo(ox + ow / 2 - 8, oy + oh / 2);
            ctx.lineTo(ox + ow / 2, oy + wingFlap);
            ctx.lineTo(ox + ow / 2 + 8, oy + oh / 2);
            ctx.stroke();

            // Optic scanner eye
            ctx.fillStyle = '#ff0055';
            ctx.beginPath();
            ctx.arc(ox + 4, oy + oh / 2, 2.5, 0, Math.PI * 2);
            ctx.fill();

          } else {
            // Neon Cactus Barrier
            const isLarge = obs.type === 'cactus_large';
            const isDouble = obs.type === 'cactus_double';
            ctx.fillStyle = isLarge ? '#ef4444' : '#10b981';
            ctx.strokeStyle = isLarge ? '#f87171' : '#34d399';
            ctx.lineWidth = 1.5;
            ctx.shadowColor = isLarge ? '#ef4444' : '#10b981';
            ctx.shadowBlur = 6;

            // Main stem
            ctx.fillRect(ox, oy, ow, oh);
            ctx.strokeRect(ox, oy, ow, oh);

            // Side branches
            if (isDouble || isLarge) {
              ctx.fillRect(ox - 4, oy + 8, 4, 12);
              ctx.fillRect(ox + ow, oy + 12, 4, 12);
            }
          }
          ctx.restore();
        }
      });

      // 4. Render Cyber-Dino
      const dinoScreenX = 40;
      const dinoScreenY = groundY - dinoY;
      const legCycle = Math.sin(tick * 0.6);

      ctx.save();
      ctx.fillStyle = modelColor;
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1.5;
      ctx.shadowColor = modelColor;
      ctx.shadowBlur = 10;

      if (isDucking) {
        // Ducking / Crouching posture
        const dw = 42;
        const dh = 20;
        const dy = dinoScreenY - dh;

        // Aerodynamic Torso
        ctx.beginPath();
        ctx.roundRect(dinoScreenX, dy, dw, dh, 4);
        ctx.fill();
        ctx.stroke();

        // Glowing Visor
        ctx.fillStyle = '#00ffff';
        ctx.fillRect(dinoScreenX + dw - 10, dy + 4, 8, 4);

        // Low thruster glow
        ctx.fillStyle = '#f59e0b';
        ctx.fillRect(dinoScreenX - 5, dy + 8, 5, 5);

      } else {
        // Standing / Running / Jumping posture
        const dw = 28;
        const dh = 36;
        const dy = dinoScreenY - dh;

        // Torso & Head
        ctx.beginPath();
        ctx.moveTo(dinoScreenX, dy + dh);
        ctx.lineTo(dinoScreenX + 8, dy + 10);
        ctx.lineTo(dinoScreenX + dw, dy);
        ctx.lineTo(dinoScreenX + dw, dy + 14);
        ctx.lineTo(dinoScreenX + 18, dy + 22);
        ctx.lineTo(dinoScreenX + 16, dy + dh);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Eye Visor
        ctx.fillStyle = '#00ffff';
        ctx.shadowColor = '#00ffff';
        ctx.shadowBlur = 8;
        ctx.fillRect(dinoScreenX + dw - 10, dy + 4, 8, 3);

        // Legs Animation
        ctx.strokeStyle = modelColor;
        ctx.lineWidth = 2;
        if (isJumping) {
          // Tucked legs + thruster particles
          ctx.beginPath();
          ctx.moveTo(dinoScreenX + 8, dinoScreenY);
          ctx.lineTo(dinoScreenX + 4, dinoScreenY + 6);
          ctx.moveTo(dinoScreenX + 14, dinoScreenY);
          ctx.lineTo(dinoScreenX + 18, dinoScreenY + 6);
          ctx.stroke();

          // Blue jet plume
          ctx.fillStyle = 'rgba(0, 243, 255, 0.8)';
          ctx.beginPath();
          ctx.arc(dinoScreenX + 10, dinoScreenY + 5, 3 + Math.random() * 2, 0, Math.PI * 2);
          ctx.fill();
        } else {
          // Running legs
          ctx.beginPath();
          ctx.moveTo(dinoScreenX + 6, dinoScreenY - 6);
          ctx.lineTo(dinoScreenX + 6 + legCycle * 8, dinoScreenY);
          ctx.moveTo(dinoScreenX + 14, dinoScreenY - 6);
          ctx.lineTo(dinoScreenX + 14 - legCycle * 8, dinoScreenY);
          ctx.stroke();
        }
      }
      ctx.restore();

      // 5. In-Canvas HUD Overlay
      ctx.save();
      ctx.font = '10px "JetBrains Mono", monospace';
      ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
      ctx.fillText(`DIST: ${Math.floor(dist)}m`, 10, 18);
      ctx.fillStyle = 'rgba(0, 243, 255, 0.9)';
      ctx.fillText(`VEL: ${speed.toFixed(1)} px/f`, width - 85, 18);

      // Action banner if event exists
      const decAction = lastEvent?.decision?.action || 'RUN';
      let actColor = '#10b981';
      if (decAction === 'JUMP') actColor = '#00f3ff';
      if (decAction === 'DUCK') actColor = '#ec4899';

      ctx.fillStyle = actColor;
      ctx.shadowColor = actColor;
      ctx.shadowBlur = 6;
      ctx.fillText(`► ${decAction}`, 10, height - 12);
      ctx.restore();

      // 6. Game Over Glitch Overlay
      if (!isAlive) {
        ctx.save();
        ctx.fillStyle = 'rgba(239, 68, 68, 0.3)';
        ctx.fillRect(0, 0, width, height);
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 2;
        ctx.strokeRect(2, 2, width - 4, height - 4);

        ctx.font = 'bold 12px "JetBrains Mono", monospace';
        ctx.fillStyle = '#ffffff';
        ctx.shadowColor = '#ef4444';
        ctx.shadowBlur = 10;
        ctx.textAlign = 'center';
        ctx.fillText('CRITICAL COLLISION', width / 2, height / 2 - 4);
        ctx.font = '10px "JetBrains Mono", monospace';
        ctx.fillStyle = '#fca5a5';
        ctx.fillText(`DISTANCE: ${Math.floor(dist)}m`, width / 2, height / 2 + 14);
        ctx.restore();
      }
    };

    render();
  }, [gameState, lastEvent, modelColor, isAlive, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{
        width: '100%',
        height: '100%',
        display: 'block',
        borderRadius: '8px',
      }}
    />
  );
}
