"use client";

import { useMemo, useState } from "react";
import {
    Lock,
    Check,
    X,
    LoaderCircle,
    Armchair,
    Sparkles,
    ArrowLeft,
    Ticket,
} from "lucide-react";
import Checkout from "@/components/checkout/Checkout";

type SeatStatus = "available" | "locked" | "booked" | "syncing";

type Seat = {
    id: string;
    status: SeatStatus;
};

type SeatMapProps = {
    eventName: string;
    price: number;
    eventDate: string;
    eventTime: string;
    venue: string;
    city: string;
};

const initialSeats: Seat[] = Array.from({ length: 40 }, (_, index) => {
    const row = String.fromCharCode(65 + Math.floor(index / 8));
    const number = (index % 8) + 1;
    const id = `${row}${number}`;

    let status: SeatStatus = "available";

    if (["A3", "A4", "B5", "C2", "D7"].includes(id)) {
        status = "booked";
    } else if (["B2", "D4"].includes(id)) {
        status = "locked";
    } else if (id === "E8") {
        status = "syncing";
    }

    return { id, status };
});

export default function SeatMap({
    eventName,
    price,
    eventDate,
    eventTime,
    venue,
    city,
}: SeatMapProps) {
    const [seats] = useState(initialSeats);
    const [selectedSeats, setSelectedSeats] = useState<string[]>([]);
    const [showCheckout, setShowCheckout] = useState(false);

    function toggleSeat(seat: Seat) {
        if (seat.status !== "available") return;

        setSelectedSeats((previous) =>
            previous.includes(seat.id)
                ? previous.filter((id) => id !== seat.id)
                : [...previous, seat.id]
        );
    }

    const totalPrice = useMemo(
        () => selectedSeats.length * price,
        [selectedSeats, price]
    );

    function clearSeats() {
        setSelectedSeats([]);
    }

    const seatStyles: Record<SeatStatus, string> = {
        available:
            "border-emerald-400/40 bg-gradient-to-br from-emerald-400/20 to-emerald-950/50 text-emerald-300 hover:border-emerald-300 hover:from-emerald-400/40 hover:to-emerald-700/30 hover:shadow-[0_0_25px_rgba(52,211,153,0.45)] hover:-translate-y-2 hover:scale-110 cursor-pointer",
        locked:
            "border-amber-400/30 bg-gradient-to-br from-amber-500/20 to-amber-950/50 text-amber-300 cursor-not-allowed opacity-80",
        booked:
            "border-red-400/30 bg-gradient-to-br from-red-500/20 to-red-950/50 text-red-300 cursor-not-allowed opacity-70",
        syncing:
            "border-sky-400/30 bg-gradient-to-br from-sky-500/20 to-sky-950/50 text-sky-300 cursor-not-allowed",
    };

    function seatIcon(status: SeatStatus) {
        if (status === "locked") return <Lock size={13} />;
        if (status === "booked") return <X size={15} />;
        if (status === "syncing") {
            return <LoaderCircle size={14} className="animate-spin" />;
        }
        return <Armchair size={15} />;
    }

    if (showCheckout) {
        return (
            <Checkout
                eventName={eventName}
                price={price}
                selectedSeats={selectedSeats}
                onBack={() => setShowCheckout(false)}
                eventDate={eventDate}
                eventTime={eventTime}
                venue={venue}
                city={city}
            />
        );
    }

    return (
        <section className="seat-experience relative my-10 overflow-hidden rounded-3xl border border-violet-500/20 bg-[#0d0b1c] p-5 text-white shadow-[0_20px_80px_rgba(0,0,0,0.4)] sm:p-8">

            <div className="pointer-events-none absolute -right-32 -top-32 h-80 w-80 rounded-full bg-violet-600/10 blur-[100px]" />
            <div className="pointer-events-none absolute -bottom-32 -left-32 h-80 w-80 rounded-full bg-indigo-600/10 blur-[100px]" />

            <div className="relative mb-8 flex flex-wrap items-start justify-between gap-4">
                <div>
                    <div className="mb-3 flex items-center gap-2 text-sm font-bold tracking-[0.2em] text-violet-400">
                        <Sparkles size={16} />
                        SEAT SELECTION
                    </div>

                    <h2 className="text-2xl font-extrabold tracking-tight sm:text-3xl">
                        Choose Your Seats
                    </h2>

                    <p className="mt-2 text-sm text-slate-400">
                        {eventName}
                    </p>
                </div>

                <div className="rounded-xl border border-violet-400/20 bg-violet-500/10 px-4 py-3">
                    <p className="text-xs text-slate-400">Price per ticket</p>
                    <p className="mt-1 text-xl font-extrabold text-violet-300">
                        ₹{price.toLocaleString("en-IN")}
                    </p>
                </div>
            </div>

            <div className="relative mb-10 flex flex-wrap justify-center gap-x-5 gap-y-3 rounded-2xl border border-white/5 bg-white/[0.03] p-4">
                <div className="flex items-center gap-2 text-xs text-slate-300">
                    <span className="h-3.5 w-3.5 rounded border border-emerald-400 bg-emerald-500/30" />
                    Available
                </div>

                <div className="flex items-center gap-2 text-xs text-slate-300">
                    <span className="h-3.5 w-3.5 rounded border border-amber-400 bg-amber-500/30" />
                    Locked
                </div>

                <div className="flex items-center gap-2 text-xs text-slate-300">
                    <span className="h-3.5 w-3.5 rounded border border-red-400 bg-red-500/30" />
                    Booked
                </div>

                <div className="flex items-center gap-2 text-xs text-slate-300">
                    <span className="h-3.5 w-3.5 rounded border border-sky-400 bg-sky-500/30" />
                    Syncing
                </div>

                <div className="flex items-center gap-2 text-xs text-slate-300">
                    <span className="h-3.5 w-3.5 rounded border border-violet-400 bg-violet-500" />
                    Selected
                </div>
            </div>

            <div className="relative mx-auto mb-14 max-w-xl">
                <div className="absolute -top-8 left-1/2 h-12 w-3/4 -translate-x-1/2 rounded-full bg-violet-500/30 blur-2xl animate-pulse" />

                <div className="relative overflow-hidden rounded-t-[50%] border-t-2 border-violet-400/80 bg-gradient-to-b from-violet-500/25 via-indigo-500/10 to-transparent px-4 pb-5 pt-5 text-center shadow-[0_-10px_40px_rgba(139,92,246,0.2)]">
                    <div className="text-xs font-bold tracking-[0.45em] text-violet-300 sm:text-sm">
                        SCREEN / STAGE
                    </div>
                    <div className="mx-auto mt-3 h-1 w-2/3 rounded-full bg-gradient-to-r from-transparent via-violet-300 to-transparent shadow-[0_0_20px_rgba(167,139,250,0.9)] animate-pulse" />
                </div>
            </div>

            <div className="relative mx-auto max-w-xl">
                <div className="mb-5 text-center text-xs font-semibold tracking-[0.3em] text-slate-500">
                    AUDITORIUM SEATING
                </div>

                <div className="space-y-4">
                    {["A", "B", "C", "D", "E"].map((row, rowIndex) => (
                        <div
                            key={row}
                            className="seat-row flex items-center justify-center gap-1.5 sm:gap-3"
                            style={{ animationDelay: `${rowIndex * 100}ms` }}
                        >
                            <span className="w-5 text-center text-xs font-bold text-violet-300 sm:w-7">
                                {row}
                            </span>

                            {seats
                                .filter((seat) => seat.id.startsWith(row))
                                .map((seat, seatIndex) => {
                                    const isSelected = selectedSeats.includes(seat.id);

                                    return (
                                        <button
                                            key={seat.id}
                                            type="button"
                                            disabled={seat.status !== "available"}
                                            onClick={() => toggleSeat(seat)}
                                            aria-label={`Seat ${seat.id}, ${isSelected ? "selected" : seat.status}`}
                                            aria-pressed={isSelected}
                                            className={`seat-button relative flex h-9 w-9 items-center justify-center rounded-lg border text-xs font-bold transition-all duration-300 ease-out sm:h-11 sm:w-11 ${isSelected
                                                    ? "selected-seat scale-110 border-violet-300 bg-gradient-to-br from-violet-400 via-violet-600 to-indigo-700 text-white shadow-[0_0_25px_rgba(139,92,246,0.7)]"
                                                    : seatStyles[seat.status]
                                                }`}
                                            style={{
                                                animationDelay: `${seatIndex * 35}ms`,
                                            }}
                                        >
                                            {isSelected ? (
                                                <Check size={16} className="animate-in" />
                                            ) : (
                                                seatIcon(seat.status)
                                            )}
                                        </button>
                                    );
                                })}

                            <span className="w-5 text-center text-xs font-bold text-violet-300 sm:w-7">
                                {row}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            <div className="relative mt-12 rounded-2xl border border-violet-400/20 bg-gradient-to-br from-[#19152f] to-[#111024] p-5 shadow-xl sm:p-6">

                <div className="mb-5 flex items-center gap-3">
                    <div className="rounded-xl bg-violet-500/15 p-3 text-violet-300">
                        <Ticket size={22} />
                    </div>

                    <div>
                        <h3 className="font-bold text-white">Booking Summary</h3>
                        <p className="text-xs text-slate-400">
                            Review your selected seats
                        </p>
                    </div>
                </div>

                <div className="space-y-4">
                    <div className="flex justify-between text-sm text-slate-400">
                        <span>Selected seats</span>
                        <span className="font-semibold text-white">
                            {selectedSeats.length}
                        </span>
                    </div>

                    <div className="flex justify-between text-sm text-slate-400">
                        <span>Price per ticket</span>
                        <span className="font-semibold text-white">
                            ₹{price.toLocaleString("en-IN")}
                        </span>
                    </div>

                    {selectedSeats.length > 0 && (
                        <div className="rounded-xl border border-violet-400/15 bg-violet-500/10 p-3">
                            <p className="mb-2 text-xs font-semibold text-violet-300">
                                YOUR SEATS
                            </p>
                            <div className="flex flex-wrap gap-2">
                                {selectedSeats.map((id) => (
                                    <span
                                        key={id}
                                        className="seat-chip rounded-md border border-violet-400/30 bg-violet-500/20 px-2.5 py-1 text-xs font-bold text-violet-200"
                                    >
                                        {id}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className="flex items-center justify-between border-t border-white/10 pt-5">
                        <span className="font-bold text-white">
                            Ticket Subtotal
                        </span>

                        <span className="text-2xl font-extrabold text-violet-300">
                            ₹{totalPrice.toLocaleString("en-IN")}
                        </span>
                    </div>
                </div>

                <div className="mt-6 flex flex-col gap-3 sm:flex-row">
                    <button
                        type="button"
                        onClick={clearSeats}
                        disabled={selectedSeats.length === 0}
                        className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-slate-300 transition duration-300 hover:-translate-y-0.5 hover:border-white/20 hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                        <ArrowLeft size={16} />
                        Clear Selection
                    </button>

                    <button
                        type="button"
                        disabled={selectedSeats.length === 0}
                        onClick={() => setShowCheckout(true)}
                        className="checkout-button flex flex-1 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-5 py-3 text-sm font-bold text-white shadow-lg shadow-violet-900/30 transition duration-300 hover:-translate-y-1 hover:shadow-violet-500/40 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:translate-y-0"
                    >
                        Continue to Checkout
                        <Ticket size={17} />
                    </button>
                </div>

                <p className="mt-4 text-center text-xs leading-relaxed text-slate-500">
                    Demo seat availability only. Seats are not reserved until
                    the backend confirms a successful booking.
                </p>
            </div>
        </section>
    );
}