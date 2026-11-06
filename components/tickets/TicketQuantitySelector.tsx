"use client";

import { useState } from "react";
import {
    Ticket,
    Minus,
    Plus,
    CalendarDays,
    MapPin,
    Clock,
    ShoppingBag,
    ArrowRight,
} from "lucide-react";

type TicketQuantitySelectorProps = {
    eventName: string;
    price: number;
    eventDate: string;
    eventTime: string;
    venue: string;
    city: string;
    onContinue: (quantity: number) => void;
};

export default function TicketQuantitySelector({
    eventName,
    price,
    eventDate,
    eventTime,
    venue,
    city,
    onContinue,
}: TicketQuantitySelectorProps) {
    const [quantity, setQuantity] = useState(1);

    // Temporary frontend demo limit.
    const maxTickets = 10;

    const total = price * quantity;

    return (
        <section className="overflow-hidden rounded-2xl border border-violet-400/20 bg-[#131326] shadow-2xl shadow-violet-950/20">

            <div className="border-b border-white/10 bg-gradient-to-r from-violet-700/20 to-indigo-700/20 p-5 sm:p-7">
                <div className="flex items-center gap-3">
                    <div className="rounded-xl bg-violet-500/20 p-3 text-violet-300">
                        <Ticket size={25} />
                    </div>

                    <div>
                        <p className="text-sm font-semibold text-violet-400">
                            GENERAL ADMISSION
                        </p>

                        <h2 className="text-xl font-extrabold text-white sm:text-2xl">
                            Select Your Tickets
                        </h2>
                    </div>
                </div>

                <p className="mt-3 text-sm text-slate-400">
                    Choose how many tickets you want. No individual seat selection is required.
                </p>
            </div>

            <div className="grid gap-6 p-5 sm:p-7 md:grid-cols-2">

                <div>
                    <h3 className="text-lg font-bold text-white">
                        {eventName}
                    </h3>

                    <div className="mt-4 space-y-3 text-sm text-slate-400">
                        <p className="flex items-center gap-2">
                            <CalendarDays size={17} className="text-violet-400" />
                            {eventDate}
                        </p>

                        <p className="flex items-center gap-2">
                            <Clock size={17} className="text-violet-400" />
                            {eventTime}
                        </p>

                        <p className="flex items-center gap-2">
                            <MapPin size={17} className="text-violet-400" />
                            {venue}, {city}
                        </p>
                    </div>

                    <div className="mt-6 rounded-xl border border-violet-400/20 bg-violet-500/10 p-4">
                        <p className="text-sm text-slate-400">
                            Price per ticket
                        </p>

                        <p className="mt-1 text-2xl font-extrabold text-violet-300">
                            ₹{price.toLocaleString("en-IN")}
                        </p>
                    </div>
                </div>

                <div className="flex flex-col justify-center rounded-xl border border-white/10 bg-[#0c0c1c] p-5">

                    <p className="text-sm font-semibold text-slate-300">
                        Number of tickets
                    </p>

                    <div className="mt-4 flex items-center justify-between gap-3">

                        <button
                            type="button"
                            onClick={() =>
                                setQuantity((previous) =>
                                    Math.max(1, previous - 1)
                                )
                            }
                            disabled={quantity <= 1}
                            aria-label="Decrease ticket quantity"
                            className="rounded-xl border border-white/10 bg-[#202039] p-3 text-white transition hover:border-violet-400 disabled:cursor-not-allowed disabled:opacity-30"
                        >
                            <Minus size={20} />
                        </button>

                        <span className="min-w-12 text-center text-3xl font-extrabold text-white">
                            {quantity}
                        </span>

                        <button
                            type="button"
                            onClick={() =>
                                setQuantity((previous) =>
                                    Math.min(maxTickets, previous + 1)
                                )
                            }
                            disabled={quantity >= maxTickets}
                            aria-label="Increase ticket quantity"
                            className="rounded-xl border border-white/10 bg-[#202039] p-3 text-white transition hover:border-violet-400 disabled:cursor-not-allowed disabled:opacity-30"
                        >
                            <Plus size={20} />
                        </button>
                    </div>

                    <p className="mt-3 text-xs text-slate-500">
                        Demo limit: maximum {maxTickets} tickets per selection.
                    </p>

                    <div className="mt-6 border-t border-white/10 pt-5">
                        <div className="flex items-center justify-between text-sm text-slate-400">
                            <span>
                                {quantity} × ₹{price.toLocaleString("en-IN")}
                            </span>

                            <span>
                                ₹{total.toLocaleString("en-IN")}
                            </span>
                        </div>

                        <div className="mt-3 flex items-center justify-between">
                            <span className="font-semibold text-white">
                                Total amount
                            </span>

                            <span className="text-2xl font-extrabold text-violet-300">
                                ₹{total.toLocaleString("en-IN")}
                            </span>
                        </div>
                    </div>

                    <div className="mt-5 flex items-center justify-center gap-2 rounded-xl bg-violet-600/15 px-4 py-3 text-sm font-semibold text-violet-300">
                        <ShoppingBag size={17} />
                        Tickets selected: {quantity}
                    </div>

                    <button
                        type="button"
                        onClick={() => onContinue(quantity)}
                        className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-5 py-4 font-bold text-white shadow-lg shadow-violet-900/30 transition hover:-translate-y-1 hover:shadow-violet-500/30"
                    >
                        Continue to Checkout
                        <ArrowRight size={18} />
                    </button>
                </div>
            </div>
        </section>
    );
}