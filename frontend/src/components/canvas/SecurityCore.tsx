import React, { useRef, useMemo, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { AppState } from '../../types';

interface SecurityCoreProps {
  appState: AppState;
  lowPowerMode: boolean;
}

// Procedural 3D Mesh Component
function CoreMesh({ appState }: { appState: AppState }) {
  const innerMeshRef = useRef<THREE.Mesh>(null);
  const outerCageRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);
  const particlesRef = useRef<THREE.Points>(null);

  // Mouse parallax coordinates
  const mouse = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      mouse.current.x = (e.clientX / window.innerWidth - 0.5) * 2;
      mouse.current.y = -(e.clientY / window.innerHeight - 0.5) * 2;
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Generate floating particle positions
  const particlePositions = useMemo(() => {
    const count = 120;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 7;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 7;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 7;
    }
    return positions;
  }, []);

  // State-driven color definitions
  const stateColor = useMemo(() => {
    switch (appState) {
      case 'VERIFIED':
        return new THREE.Color('#10b981'); // Emerald Green
      case 'SUSPICIOUS':
        return new THREE.Color('#f59e0b'); // Amber Gold
      case 'CRITICAL_FRAUD':
        return new THREE.Color('#ef4444'); // Crimson Red
      case 'SCANNING':
        return new THREE.Color('#06b6d4'); // Electric Cyan
      case 'IDLE':
      default:
        return new THREE.Color('#38bdf8'); // Sky Ice Blue
    }
  }, [appState]);

  useFrame((state, delta) => {
    const time = state.clock.getElapsedTime();

    if (innerMeshRef.current && outerCageRef.current && ringRef.current) {
      // 1. Lissajous Curve Floating Idle Animation
      const floatX = Math.sin(time * 0.8) * 0.15;
      const floatY = Math.cos(time * 0.6) * 0.2;
      innerMeshRef.current.position.y = floatY;
      outerCageRef.current.position.y = floatY;

      // 2. Parallax Lerp from Mouse
      const targetRotX = mouse.current.y * 0.3;
      const targetRotY = mouse.current.x * 0.3;
      innerMeshRef.current.rotation.x = THREE.MathUtils.lerp(innerMeshRef.current.rotation.x, targetRotX, delta * 2.5);
      innerMeshRef.current.rotation.y = THREE.MathUtils.lerp(innerMeshRef.current.rotation.y, targetRotY, delta * 2.5);

      // 3. State-dependent rotation & dynamics
      if (appState === 'SCANNING') {
        innerMeshRef.current.rotation.y += delta * 4.0;
        outerCageRef.current.rotation.x -= delta * 3.0;
        outerCageRef.current.rotation.z += delta * 2.5;
        ringRef.current.scale.setScalar(1.0 + Math.sin(time * 10.0) * 0.3);
      } else if (appState === 'CRITICAL_FRAUD') {
        // Halt and pulse violently
        innerMeshRef.current.rotation.y = Math.sin(time * 25.0) * 0.1;
        outerCageRef.current.rotation.z = Math.cos(time * 20.0) * 0.15;
        const scalePulse = 1.0 + Math.sin(time * 15.0) * 0.08;
        innerMeshRef.current.scale.setScalar(scalePulse);
      } else {
        // Counter-rotating orbital inertia
        innerMeshRef.current.rotation.y += delta * 0.4;
        outerCageRef.current.rotation.y -= delta * 0.3;
        outerCageRef.current.rotation.z += delta * 0.1;
        ringRef.current.scale.setScalar(1.0 + Math.sin(time * 1.5) * 0.05);
      }

      // Smooth color transitions
      const innerMat = innerMeshRef.current.material as THREE.MeshStandardMaterial;
      if (innerMat && innerMat.color) {
        innerMat.color.lerp(stateColor, delta * 4.0);
        innerMat.emissive.lerp(stateColor, delta * 4.0);
      }

      const cageMat = outerCageRef.current.material as THREE.MeshStandardMaterial;
      if (cageMat && cageMat.color) {
        cageMat.color.lerp(stateColor, delta * 4.0);
      }
    }

    // Particle Swarm Rotation
    if (particlesRef.current) {
      particlesRef.current.rotation.y += delta * (appState === 'SCANNING' ? 0.8 : 0.05);
    }
  });

  return (
    <group>
      {/* Ambient & Point Lights */}
      <ambientLight intensity={0.4} />
      <pointLight position={[5, 5, 5]} intensity={1.5} color={stateColor} />
      <pointLight position={[-5, -5, -5]} intensity={0.8} color="#ffffff" />

      {/* Inner Metallic Icosahedron Core */}
      <mesh ref={innerMeshRef} scale={1.2}>
        <icosahedronGeometry args={[1, 1]} />
        <meshStandardMaterial
          roughness={0.2}
          metalness={0.85}
          wireframe={appState === 'CRITICAL_FRAUD'}
          emissive={stateColor}
          emissiveIntensity={appState === 'CRITICAL_FRAUD' ? 0.9 : appState === 'SCANNING' ? 0.7 : 0.35}
        />
      </mesh>

      {/* Outer Wireframe Cage Ring */}
      <mesh ref={outerCageRef} scale={1.8}>
        <icosahedronGeometry args={[1, 2]} />
        <meshStandardMaterial
          wireframe
          transparent
          opacity={0.6}
          color={stateColor}
          roughness={0.1}
          metalness={0.9}
        />
      </mesh>

      {/* Radar Sweep Orbital Torus Ring */}
      <mesh ref={ringRef} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[2.2, 0.02, 16, 100]} />
        <meshBasicMaterial color={stateColor} transparent opacity={0.7} />
      </mesh>

      {/* Floating Dust Particle Swarm */}
      <points ref={particlesRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[particlePositions, 3]}
          />
        </bufferGeometry>

        <pointsMaterial
          size={0.04}
          color={stateColor}
          transparent
          opacity={0.6}
          sizeAttenuation
        />
      </points>
    </group>
  );
}

// Low Power Fallback SVG Component
function LowPowerFallback({ appState }: { appState: AppState }) {
  const getGlowColor = () => {
    switch (appState) {
      case 'VERIFIED':
        return 'from-emerald-500/40 via-emerald-600/20 to-transparent shadow-emerald-500/50';
      case 'SUSPICIOUS':
        return 'from-amber-500/40 via-amber-600/20 to-transparent shadow-amber-500/50';
      case 'CRITICAL_FRAUD':
        return 'from-rose-500/50 via-rose-600/30 to-transparent shadow-rose-500/60 animate-pulse';
      case 'SCANNING':
        return 'from-cyan-500/50 via-cyan-600/20 to-transparent shadow-cyan-500/50 animate-spin-slow';
      case 'IDLE':
      default:
        return 'from-sky-500/30 via-indigo-600/20 to-transparent shadow-sky-500/30';
    }
  };

  return (
    <div className="relative w-full h-full flex items-center justify-center overflow-hidden">
      <div
        className={`w-48 h-48 rounded-full bg-gradient-to-tr ${getGlowColor()} filter blur-2xl transition-all duration-700 opacity-80`}
      />
      <div className="absolute inset-0 flex items-center justify-center">
        <svg className="w-32 h-32 text-zinc-300 stroke-cyan-400" viewBox="0 0 100 100">
          <polygon
            points="50,15 85,35 85,75 50,95 15,75 15,35"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            className={appState === 'SCANNING' ? 'animate-spin' : ''}
          />
          <polygon
            points="50,25 75,40 75,70 50,85 25,70 25,40"
            fill="none"
            stroke="cyan"
            strokeWidth="1"
            opacity="0.8"
          />
        </svg>
      </div>
    </div>
  );
}

export const SecurityCore: React.FC<SecurityCoreProps> = ({ appState, lowPowerMode }) => {
  if (lowPowerMode) {
    return <LowPowerFallback appState={appState} />;
  }

  return (
    <div className="w-full h-full relative cursor-grab active:cursor-grabbing">
      <Canvas
        dpr={[1, 1.5]}
        gl={{ powerPreference: 'high-performance', antialias: true }}
        camera={{ position: [0, 0, 5.5], fov: 50 }}
      >
        <CoreMesh appState={appState} />
      </Canvas>
    </div>
  );
};
