
"use client";

import { useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import {
    RoundedBox,
    Stars,
    Float,
    Sparkles,
} from "@react-three/drei";
import type { Group, Mesh } from "three";

function FloatingTicket({
    position,
    color,
    speed,
    scale = 1,
}: {
    position: [number, number, number];
    color: string;
    speed: number;
    scale?: number;
}) {
    const ticketRef = useRef<Group>(null);

    useFrame((state) => {
        if (!ticketRef.current) return;

        const time = state.clock.elapsedTime;

        ticketRef.current.rotation.y =
            Math.sin(time * speed) * 0.35;

        ticketRef.current.rotation.x =
            Math.cos(time * speed * 0.7) * 0.12;

        ticketRef.current.position.y =
            position[1] + Math.sin(time * speed * 1.5) * 0.2;
    });

    return (
        <group ref={ticketRef} position={position} scale={scale}>
            {/* Main ticket */}
            <RoundedBox
                args={[2.1, 1.2, 0.14]}
                radius={0.13}
                smoothness={6}
            >
                <meshPhysicalMaterial
                    color={color}
                    metalness={0.65}
                    roughness={0.22}
                    clearcoat={1}
                    clearcoatRoughness={0.15}
                    emissive={color}
                    emissiveIntensity={0.18}
                />
            </RoundedBox>

            {/* Ticket highlight */}
            <mesh position={[0, 0, 0.078]}>
                <planeGeometry args={[1.9, 1.02]} />
                <meshBasicMaterial
                    color="#ffffff"
                    transparent
                    opacity={0.035}
                />
            </mesh>

            {/* Perforated center line */}
            <mesh position={[0.42, 0, 0.09]}>
                <boxGeometry args={[0.018, 0.9, 0.015]} />
                <meshBasicMaterial color="#ffffff" />
            </mesh>

            {/* Left side ticket symbol */}
            <mesh position={[-0.55, 0.25, 0.1]}>
                <boxGeometry args={[0.55, 0.07, 0.02]} />
                <meshBasicMaterial color="#ffffff" />
            </mesh>

            <mesh position={[-0.55, 0.05, 0.1]}>
                <boxGeometry args={[0.75, 0.035, 0.02]} />
                <meshBasicMaterial color="#ddd6fe" />
            </mesh>

            <mesh position={[-0.55, -0.1, 0.1]}>
                <boxGeometry args={[0.6, 0.035, 0.02]} />
                <meshBasicMaterial color="#ddd6fe" />
            </mesh>

            <mesh position={[-0.55, -0.25, 0.1]}>
                <boxGeometry args={[0.42, 0.035, 0.02]} />
                <meshBasicMaterial color="#ddd6fe" />
            </mesh>

            {/* Barcode */}
            {Array.from({ length: 9 }, (_, index) => (
                <mesh
                    key={index}
                    position={[
                        0.7 + index * 0.045,
                        0,
                        0.1,
                    ]}
                >
                    <boxGeometry
                        args={[
                            index % 3 === 0 ? 0.025 : 0.012,
                            0.48,
                            0.018,
                        ]}
                    />
                    <meshBasicMaterial color="#ffffff" />
                </mesh>
            ))}

            {/* Ticket glow details */}
            <pointLight
                position={[0, 0, 0.8]}
                intensity={1.5}
                distance={3}
                color={color}
            />
        </group>
    );
}

function RotatingRings() {
    const ringRef = useRef<Group>(null);

    useFrame((state) => {
        if (!ringRef.current) return;

        const time = state.clock.elapsedTime;

        ringRef.current.rotation.z = time * 0.2;
        ringRef.current.rotation.x =
            Math.sin(time * 0.4) * 0.18;
        ringRef.current.rotation.y =
            Math.cos(time * 0.3) * 0.15;
    });

    return (
        <group ref={ringRef} position={[0.2, 0, -1.5]}>
            <mesh>
                <torusGeometry args={[2.05, 0.018, 16, 120]} />
                <meshBasicMaterial
                    color="#a78bfa"
                    toneMapped={false}
                />
            </mesh>

            <mesh rotation={[0.7, 0.4, 0.5]}>
                <torusGeometry args={[2.35, 0.014, 16, 120]} />
                <meshBasicMaterial
                    color="#ec4899"
                    toneMapped={false}
                />
            </mesh>

            <mesh rotation={[1.1, 0.3, 0.2]}>
                <torusGeometry args={[2.65, 0.012, 16, 120]} />
                <meshBasicMaterial
                    color="#818cf8"
                    toneMapped={false}
                />
            </mesh>

            <mesh rotation={[0.4, 1, 0.8]}>
                <torusGeometry args={[2.85, 0.009, 16, 120]} />
                <meshBasicMaterial
                    color="#f0abfc"
                    toneMapped={false}
                />
            </mesh>
        </group>
    );
}

function AnimatedStage() {
    const stageRef = useRef<Group>(null);

    useFrame((state) => {
        if (!stageRef.current) return;

        const time = state.clock.elapsedTime;

        stageRef.current.position.y =
            -1.25 + Math.sin(time * 1.2) * 0.05;

        stageRef.current.rotation.y =
            Math.sin(time * 0.3) * 0.08;
    });

    return (
        <group ref={stageRef} position={[0, -1.25, -1]}>
            {/* Main stage base */}
            <mesh>
                <cylinderGeometry args={[2, 2.3, 0.22, 80]} />
                <meshPhysicalMaterial
                    color="#21154a"
                    metalness={0.85}
                    roughness={0.2}
                    clearcoat={1}
                />
            </mesh>

            {/* Glowing stage ring */}
            <mesh position={[0, 0.13, 0]}>
                <cylinderGeometry args={[1.8, 1.85, 0.07, 80]} />
                <meshStandardMaterial
                    color="#7c3aed"
                    emissive="#7c3aed"
                    emissiveIntensity={2}
                    metalness={0.7}
                />
            </mesh>

            {/* Center platform */}
            <mesh position={[0, 0.23, 0]}>
                <cylinderGeometry args={[1.35, 1.55, 0.13, 80]} />
                <meshStandardMaterial
                    color="#4338ca"
                    emissive="#4f46e5"
                    emissiveIntensity={0.8}
                    metalness={0.8}
                    roughness={0.2}
                />
            </mesh>

            {/* Central holographic pillar */}
            <mesh position={[0, 0.8, -0.15]}>
                <boxGeometry args={[0.85, 0.9, 0.08]} />
                <meshPhysicalMaterial
                    color="#8b5cf6"
                    emissive="#7c3aed"
                    emissiveIntensity={2}
                    transparent
                    opacity={0.75}
                    metalness={0.6}
                    roughness={0.15}
                />
            </mesh>

            <pointLight
                position={[0, 1.1, 0.5]}
                color="#a78bfa"
                intensity={8}
                distance={4}
            />
        </group>
    );
}

function FloatingShape({
    position,
    color,
    size,
}: {
    position: [number, number, number];
    color: string;
    size: number;
}) {
    const shapeRef = useRef<Mesh>(null);

    useFrame((state) => {
        if (!shapeRef.current) return;

        const time = state.clock.elapsedTime;

        shapeRef.current.rotation.x = time * 0.4;
        shapeRef.current.rotation.y = time * 0.6;

        shapeRef.current.position.y =
            position[1] + Math.sin(time * 1.3 + position[0]) * 0.18;
    });

    return (
        <mesh ref={shapeRef} position={position}>
            <icosahedronGeometry args={[size, 1]} />
            <meshPhysicalMaterial
                color={color}
                metalness={0.8}
                roughness={0.15}
                clearcoat={1}
                emissive={color}
                emissiveIntensity={0.5}
            />
        </mesh>
    );
}

function Scene() {
    useFrame((state) => {
        const time = state.clock.elapsedTime;

        state.camera.position.x =
            Math.sin(time * 0.2) * 0.12;

        state.camera.position.y =
            0.5 + Math.sin(time * 0.25) * 0.08;

        state.camera.lookAt(0, 0, 0);
    });

    return (
        <>
            {/* Lighting */}
            <ambientLight intensity={1.1} />

            <directionalLight
                position={[4, 6, 5]}
                intensity={2.5}
                color="#ffffff"
            />

            <pointLight
                position={[-4, 2, 3]}
                intensity={25}
                color="#8b5cf6"
            />

            <pointLight
                position={[4, 2, -2]}
                intensity={25}
                color="#ec4899"
            />

            <pointLight
                position={[0, -2, 3]}
                intensity={12}
                color="#6366f1"
            />

            {/* Background stars */}
            <Stars
                radius={45}
                depth={40}
                count={1400}
                factor={4}
                saturation={0.5}
                fade
                speed={1.5}
            />

            {/* Particle effects */}
            <Sparkles
                count={150}
                scale={7}
                size={3}
                speed={0.7}
                color="#c4b5fd"
            />

            <Sparkles
                count={70}
                scale={5}
                size={2}
                speed={1}
                color="#f0abfc"
            />

            {/* 3D objects */}
            <AnimatedStage />
            <RotatingRings />

            <FloatingShape
                position={[-2, 0.6, -0.5]}
                color="#ec4899"
                size={0.32}
            />

            <FloatingShape
                position={[2.3, -0.1, -0.8]}
                color="#818cf8"
                size={0.24}
            />

            <FloatingShape
                position={[-1.6, -1, 0.2]}
                color="#a78bfa"
                size={0.18}
            />

            {/* Main floating ticket */}
            <Float
                speed={2}
                rotationIntensity={0.15}
                floatIntensity={0.25}
            >
                <FloatingTicket
                    position={[1.25, 0.45, 0.3]}
                    color="#7c3aed"
                    speed={0.8}
                    scale={1}
                />
            </Float>

            {/* Secondary floating ticket */}
            <Float
                speed={1.6}
                rotationIntensity={0.2}
                floatIntensity={0.35}
            >
                <FloatingTicket
                    position={[-1.65, 0.8, -0.8]}
                    color="#db2777"
                    speed={0.6}
                    scale={0.55}
                />
            </Float>
        </>
    );
}

export default function HeroScene() {
    return (
        <div className="relative h-[350px] w-full overflow-hidden sm:h-[450px] lg:h-[540px]">
            {/* Background glow */}
            <div className="pointer-events-none absolute inset-0 rounded-full bg-violet-600/10 blur-3xl" />

            <div className="pointer-events-none absolute left-1/2 top-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2 rounded-full bg-fuchsia-500/10 blur-[90px]" />

            <Canvas
                camera={{
                    position: [0, 0.5, 7],
                    fov: 45,
                }}
                dpr={[1, 1.5]}
                gl={{
                    antialias: true,
                    alpha: true,
                    powerPreference: "high-performance",
                }}
            >
                <Scene />
            </Canvas>
        </div>
    );
}
