
"use client";

import { useState, type FormEvent } from "react";
import {
    ArrowLeft,
    CreditCard,
    Ticket,
    User,
    Mail,
    Phone,
    ShieldCheck,
} from "lucide-react";

import BookingConfirmation, {
    BookingDetails,
} from "@/components/checkout/BookingConfirmation";

type CheckoutProps = {
    eventName: string;
    price: number;
    quantity?: number;
    onBack: () => void;
    eventDate: string;
    eventTime: string;
    venue: string;
    city: string;
};

type FormErrors = {
    customerName?: string;
    email?: string;
    phone?: string;
};

export default function Checkout({
    eventName,
    price,
    quantity = 0,
    onBack,
    eventDate,
    eventTime,
    venue,
    city,
}: CheckoutProps) {
    const [customerName, setCustomerName] = useState("");
    const [email, setEmail] = useState("");
    const [phone, setPhone] = useState("");
    const [errors, setErrors] = useState<FormErrors>({});
    const [booking, setBooking] = useState<BookingDetails | null>(null);

    const ticketCount = quantity;
    const subtotal = ticketCount * price;
    const convenienceFee = ticketCount * 30;
    const total = subtotal + convenienceFee;

    function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();

        const newErrors: FormErrors = {};

        if (!customerName.trim()) {
            newErrors.customerName = "Please enter your full name.";
        }

        if (!email.trim()) {
            newErrors.email = "Please enter your email address.";
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            newErrors.email = "Please enter a valid email address.";
        }

        if (!phone.trim()) {
            newErrors.phone = "Please enter your phone number.";
        } else if (!/^[0-9]{10}$/.test(phone)) {
            newErrors.phone = "Phone number must contain exactly 10 digits.";
        }

        setErrors(newErrors);

        if (Object.keys(newErrors).length > 0 || ticketCount < 1) {
            return;
        }

        const newBooking: BookingDetails = {
            bookingId: `DEMO-${Date.now().toString().slice(-8)}`,
            eventName,
            eventDate,
            eventTime,
            venue,
            city,
            customerName: customerName.trim(),
            email: email.trim(),
            phone,
            quantity: ticketCount,
            price,
            convenienceFee,
            total,
        };

        setBooking(newBooking);
    }

    function clearError(field: keyof FormErrors) {
        setErrors((previous) => ({
            ...previous,
            [field]: undefined,
        }));
    }

    if (booking) {
        return (
            <BookingConfirmation
                booking={booking}
                onBackHome={onBack}
            />
        );
    }

    return (
        <section className="checkout-experience relative my-10 overflow-hidden rounded-3xl border border-violet-500/20 bg-[#0d0b1c] p-5 text-white shadow-[0_20px_80px_rgba(0,0,0,0.4)] sm:p-8">
            <div className="pointer-events-none absolute -right-32 -top-32 h-80 w-80 rounded-full bg-violet-600/15 blur-[100px]" />
            <div className="pointer-events-none absolute -bottom-32 -left-32 h-80 w-80 rounded-full bg-indigo-600/15 blur-[100px]" />

            <button
                type="button"
                onClick={onBack}
                className="relative mb-8 flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-semibold text-slate-300 transition duration-300 hover:-translate-x-1 hover:border-violet-400/40 hover:bg-violet-500/10 hover:text-white"
            >
                <ArrowLeft size={17} />
                Back to Ticket Selection
            </button>

            <div className="checkout-heading relative mb-8">
                <div className="mb-3 flex items-center gap-2 text-sm font-bold tracking-[0.2em] text-violet-400">
                    <Ticket size={16} />
                    SECURE CHECKOUT
                </div>

                <h2 className="text-2xl font-extrabold sm:text-3xl">
                    Complete Your Booking
                </h2>

                <p className="mt-2 text-sm text-slate-400">
                    Enter your details and review your ticket information.
                </p>
            </div>

            <div className="relative grid gap-8 lg:grid-cols-2">
                <form
                    onSubmit={handleSubmit}
                    noValidate
                    className="checkout-form space-y-6"
                >
                    <div className="flex items-center gap-3">
                        <div className="rounded-xl bg-violet-500/15 p-3 text-violet-300">
                            <User size={21} />
                        </div>

                        <div>
                            <h3 className="font-bold text-white">
                                Customer Information
                            </h3>
                            <p className="text-xs text-slate-400">
                                Your contact details
                            </p>
                        </div>
                    </div>

                    <div>
                        <label
                            htmlFor="customerName"
                            className="mb-2 block text-sm font-semibold text-slate-300"
                        >
                            Full name <span className="text-red-400">*</span>
                        </label>

                        <div className="checkout-input flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.04] px-4 transition duration-300 focus-within:border-violet-400/70 focus-within:bg-violet-500/[0.06] focus-within:ring-2 focus-within:ring-violet-500/20">
                            <User size={18} className="shrink-0 text-violet-400" />

                            <input
                                id="customerName"
                                type="text"
                                required
                                maxLength={100}
                                value={customerName}
                                onChange={(event) => {
                                    setCustomerName(event.target.value);
                                    clearError("customerName");
                                }}
                                aria-invalid={Boolean(errors.customerName)}
                                aria-describedby={
                                    errors.customerName
                                        ? "customerName-error"
                                        : undefined
                                }
                                placeholder="Enter your full name"
                                autoComplete="name"
                                className="w-full bg-transparent py-3.5 text-sm text-white outline-none placeholder:text-slate-500"
                            />
                        </div>

                        {errors.customerName && (
                            <p
                                id="customerName-error"
                                role="alert"
                                className="mt-2 text-xs text-red-400"
                            >
                                {errors.customerName}
                            </p>
                        )}
                    </div>

                    <div>
                        <label
                            htmlFor="email"
                            className="mb-2 block text-sm font-semibold text-slate-300"
                        >
                            Email address <span className="text-red-400">*</span>
                        </label>

                        <div className="checkout-input flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.04] px-4 transition duration-300 focus-within:border-violet-400/70 focus-within:bg-violet-500/[0.06] focus-within:ring-2 focus-within:ring-violet-500/20">
                            <Mail size={18} className="shrink-0 text-violet-400" />

                            <input
                                id="email"
                                type="email"
                                required
                                value={email}
                                onChange={(event) => {
                                    setEmail(event.target.value);
                                    clearError("email");
                                }}
                                aria-invalid={Boolean(errors.email)}
                                aria-describedby={
                                    errors.email ? "email-error" : undefined
                                }
                                placeholder="example@email.com"
                                autoComplete="email"
                                className="w-full bg-transparent py-3.5 text-sm text-white outline-none placeholder:text-slate-500"
                            />
                        </div>

                        {errors.email && (
                            <p
                                id="email-error"
                                role="alert"
                                className="mt-2 text-xs text-red-400"
                            >
                                {errors.email}
                            </p>
                        )}
                    </div>

                    <div>
                        <label
                            htmlFor="phone"
                            className="mb-2 block text-sm font-semibold text-slate-300"
                        >
                            Phone number <span className="text-red-400">*</span>
                        </label>

                        <div className="checkout-input flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.04] px-4 transition duration-300 focus-within:border-violet-400/70 focus-within:bg-violet-500/[0.06] focus-within:ring-2 focus-within:ring-violet-500/20">
                            <Phone size={18} className="shrink-0 text-violet-400" />

                            <input
                                id="phone"
                                type="tel"
                                required
                                inputMode="numeric"
                                pattern="[0-9]{10}"
                                maxLength={10}
                                value={phone}
                                onChange={(event) => {
                                    setPhone(event.target.value);
                                    clearError("phone");
                                }}
                                aria-invalid={Boolean(errors.phone)}
                                aria-describedby={
                                    errors.phone ? "phone-error" : "phone-help"
                                }
                                placeholder="10-digit mobile number"
                                autoComplete="tel"
                                className="w-full bg-transparent py-3.5 text-sm text-white outline-none placeholder:text-slate-500"
                            />
                        </div>

                        {errors.phone ? (
                            <p
                                id="phone-error"
                                role="alert"
                                className="mt-2 text-xs text-red-400"
                            >
                                {errors.phone}
                            </p>
                        ) : (
                            <p
                                id="phone-help"
                                className="mt-2 text-xs text-slate-500"
                            >
                                Enter a 10-digit mobile number.
                            </p>
                        )}
                    </div>

                    <div aria-live="polite" aria-atomic="true" className="sr-only">
                        {Object.values(errors).filter(Boolean).join(" ")}
                    </div>

                    <button
                        type="submit"
                        disabled={ticketCount < 1}
                        className="checkout-pay group flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 bg-[length:200%_200%] px-5 py-4 font-bold text-white shadow-lg shadow-violet-900/30 transition duration-300 hover:-translate-y-1 hover:shadow-[0_10px_35px_rgba(139,92,246,0.35)] disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        <CreditCard size={19} />
                        Confirm Demo Booking
                        <span className="transition-transform group-hover:translate-x-1">
                            →
                        </span>
                    </button>

                    <div className="flex items-center justify-center gap-2 text-xs text-slate-500">
                        <ShieldCheck size={16} className="text-emerald-400" />
                        Demo checkout · No real payment processed
                    </div>
                </form>

                <div className="checkout-summary h-fit rounded-2xl border border-violet-400/20 bg-gradient-to-br from-[#19152f] to-[#111024] p-5 shadow-xl sm:p-6">
                    <div className="mb-6 flex items-center gap-3">
                        <div className="rounded-xl bg-violet-500/15 p-3 text-violet-300">
                            <Ticket size={22} />
                        </div>

                        <div>
                            <h3 className="font-bold text-white">
                                Order Summary
                            </h3>
                            <p className="text-xs text-slate-400">
                                Your ticket details
                            </p>
                        </div>
                    </div>

                    <div className="rounded-xl border border-violet-400/15 bg-violet-500/10 p-4">
                        <p className="text-xs font-semibold tracking-wider text-violet-300">
                            EVENT
                        </p>

                        <h4 className="mt-2 text-lg font-bold text-white">
                            {eventName}
                        </h4>

                        <div className="mt-3 space-y-1 text-sm text-slate-400">
                            <p>Date: {eventDate}</p>
                            <p>Time: {eventTime}</p>
                            <p>Venue: {venue}</p>
                            <p>City: {city}</p>
                        </div>

                        <p className="mt-3 text-sm font-semibold text-violet-300">
                            General Admission · {ticketCount} ticket(s)
                        </p>
                    </div>

                    <div className="mt-7 space-y-4">
                        <div className="flex justify-between text-sm text-slate-400">
                            <span>Price per ticket</span>
                            <span className="font-semibold text-white">
                                ₹{price.toLocaleString("en-IN")}
                            </span>
                        </div>

                        <div className="flex justify-between text-sm text-slate-400">
                            <span>Ticket quantity</span>
                            <span className="font-semibold text-white">
                                {ticketCount}
                            </span>
                        </div>

                        <div className="flex justify-between text-sm text-slate-400">
                            <span>Ticket subtotal</span>
                            <span className="font-semibold text-white">
                                ₹{subtotal.toLocaleString("en-IN")}
                            </span>
                        </div>

                        <div className="flex justify-between text-sm text-slate-400">
                            <span>Convenience fee (demo)</span>
                            <span className="font-semibold text-white">
                                ₹{convenienceFee.toLocaleString("en-IN")}
                            </span>
                        </div>

                        <div className="border-t border-white/10 pt-5">
                            <div className="flex items-center justify-between gap-3">
                                <span className="font-bold text-white">
                                    Total Payable
                                </span>

                                <span className="checkout-total text-2xl font-extrabold text-violet-300">
                                    ₹{total.toLocaleString("en-IN")}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="mt-6 rounded-xl border border-amber-400/20 bg-amber-500/5 p-3">
                        <p className="text-xs leading-5 text-amber-200/80">
                            This is a frontend demonstration. No payment is
                            processed and no tickets are reserved.
                        </p>
                    </div>
                </div>
            </div>
        </section>
    );
}
