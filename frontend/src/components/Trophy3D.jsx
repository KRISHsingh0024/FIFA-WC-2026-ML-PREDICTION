import React, { useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

// Procedural 3D Trophy Mesh Component
function TrophyMesh({ mousePos }) {
  const groupRef = useRef()
  
  // Use React Three Fiber frame loop to animate the trophy
  useFrame((state) => {
    if (groupRef.current) {
      // Continuous slow rotation
      groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.3
      
      // Floating / bobbing up and down effect
      groupRef.current.position.y = Math.sin(state.clock.getElapsedTime() * 1.5) * 0.12
      
      // Mouse parallax logic: tilt the trophy slightly based on mouse position
      const targetRotationX = (mousePos.y * 0.15)
      const targetRotationZ = (-mousePos.x * 0.15)
      
      groupRef.current.rotation.x = THREE.MathUtils.lerp(groupRef.current.rotation.x, targetRotationX, 0.05)
      groupRef.current.rotation.z = THREE.MathUtils.lerp(groupRef.current.rotation.z, targetRotationZ, 0.05)
    }
  })

  return (
    <group ref={groupRef} position={[0, -0.2, 0]}>
      {/* ─── Base (Marble & Gold Bands) ─── */}
      <mesh position={[0, -1.3, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[0.7, 0.8, 0.3, 32]} />
        <meshStandardMaterial color="#080f18" roughness={0.6} metalness={0.1} />
      </mesh>
      
      <mesh position={[0, -1.1, 0]} castShadow>
        <cylinderGeometry args={[0.65, 0.7, 0.1, 32]} />
        <meshStandardMaterial color="#f4b942" roughness={0.15} metalness={0.9} />
      </mesh>

      <mesh position={[0, -0.9, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[0.55, 0.65, 0.3, 32]} />
        <meshStandardMaterial color="#080f18" roughness={0.6} metalness={0.1} />
      </mesh>

      <mesh position={[0, -0.7, 0]} castShadow>
        <cylinderGeometry args={[0.5, 0.55, 0.1, 32]} />
        <meshStandardMaterial color="#f4b942" roughness={0.15} metalness={0.9} />
      </mesh>

      {/* ─── Stem / Body (Abstract Figures) ─── */}
      <mesh position={[0, -0.25, 0]} castShadow>
        <cylinderGeometry args={[0.3, 0.45, 0.8, 32]} />
        <meshStandardMaterial color="#f4b942" roughness={0.1} metalness={0.95} />
      </mesh>

      {/* Upper tapered section */}
      <mesh position={[0, 0.4, 0]} castShadow>
        <cylinderGeometry args={[0.48, 0.25, 0.6, 32]} />
        <meshStandardMaterial color="#f4b942" roughness={0.1} metalness={0.95} />
      </mesh>

      {/* Tilted Torus segments representing abstract arms holding the globe */}
      <group position={[0, 0.65, 0]}>
        <mesh rotation={[0.4, 0, 0.3]} castShadow>
          <torusGeometry args={[0.38, 0.1, 16, 32, Math.PI * 1.2]} />
          <meshStandardMaterial color="#f4b942" roughness={0.1} metalness={0.95} />
        </mesh>
        <mesh rotation={[-0.4, 0, -0.3]} castShadow>
          <torusGeometry args={[0.38, 0.1, 16, 32, Math.PI * 1.2]} />
          <meshStandardMaterial color="#f4b942" roughness={0.1} metalness={0.95} />
        </mesh>
      </group>

      {/* ─── Globe (Golden Earth) ─── */}
      <mesh position={[0, 0.95, 0]} castShadow>
        <sphereGeometry args={[0.42, 32, 32]} />
        <meshStandardMaterial color="#f4b942" roughness={0.15} metalness={0.9} />
      </mesh>

      {/* Globe Ring detail */}
      <mesh position={[0, 0.95, 0]} rotation={[Math.PI / 6, Math.PI / 4, 0]} castShadow>
        <torusGeometry args={[0.44, 0.03, 8, 32]} />
        <meshStandardMaterial color="#00e87b" roughness={0.2} metalness={0.8} />
      </mesh>
    </group>
  )
}

// Swirling Neon Particles trail around the trophy
function ParticleTrail() {
  const pointsRef = useRef()
  const count = 180
  
  const [positions] = useState(() => {
    const arr = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 10 // Spiral path
      const radius = 0.8 + Math.random() * 0.6
      arr[i * 3] = Math.cos(angle) * radius
      arr[i * 3 + 1] = (i / count) * 3.2 - 1.6 + (Math.random() - 0.5) * 0.15 // Height spread
      arr[i * 3 + 2] = Math.sin(angle) * radius
    }
    return arr
  })

  useFrame((state) => {
    if (pointsRef.current) {
      // Counter-rotate the particle swarm slowly
      pointsRef.current.rotation.y = -state.clock.getElapsedTime() * 0.25
      
      // Move particles upward and wrap them around to the bottom
      const posAttr = pointsRef.current.geometry.attributes.position
      const arr = posAttr.array
      
      for (let i = 0; i < count; i++) {
        arr[i * 3 + 1] += 0.006 // vertical speed
        
        // Wrap-around
        if (arr[i * 3 + 1] > 1.8) {
          arr[i * 3 + 1] = -1.6
        }
      }
      posAttr.needsUpdate = true
    }
  })

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute 
          attach="attributes-position"
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial 
        size={0.05} 
        color="#00e87b" 
        transparent 
        opacity={0.85}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  )
}

// Main 3D Canvas Exporter
export default function Trophy3D() {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })

  const handleMouseMove = (e) => {
    // Normalize coordinates from -1 to 1
    const x = (e.clientX / window.innerWidth) * 2 - 1
    const y = -(e.clientY / window.innerHeight) * 2 + 1
    setMousePos({ x, y })
  }

  return (
    <div 
      className="w-full h-full min-h-[350px] relative cursor-grab active:cursor-grabbing select-none"
      onMouseMove={handleMouseMove}
    >
      <Canvas
        camera={{ position: [0, 0, 3.4], fov: 45 }}
        shadows
        gl={{ antialias: true }}
      >
        {/* Lights Setup */}
        <ambientLight intensity={0.5} />
        
        {/* Warm key directional light */}
        <directionalLight 
          position={[4, 5, 3]} 
          intensity={1.8} 
          color="#feffd4" 
          castShadow 
          shadow-mapSize-width={1024}
          shadow-mapSize-height={1024}
        />
        
        {/* Fill directional light */}
        <directionalLight 
          position={[-4, 3, -2]} 
          intensity={0.6} 
          color="#8fa8c0" 
        />
        
        {/* Volumetric Green Spotlight on the trophy */}
        <spotLight 
          position={[0, 6, 0]} 
          angle={0.5} 
          penumbra={1} 
          intensity={2.5} 
          color="#00e87b" 
          castShadow
        />

        {/* Back green rim glow */}
        <pointLight 
          position={[0, 0, -2]} 
          intensity={1.5} 
          color="#00e87b" 
          distance={6}
        />

        {/* Objects */}
        <TrophyMesh mousePos={mousePos} />
        <ParticleTrail />

        {/* Orbit Controls (constrained to keep trophy centered) */}
        <OrbitControls 
          enableZoom={false}
          enablePan={false}
          minPolarAngle={Math.PI / 3}
          maxPolarAngle={Math.PI * 2 / 3}
        />
      </Canvas>
    </div>
  )
}
