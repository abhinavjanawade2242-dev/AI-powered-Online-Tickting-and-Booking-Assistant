
"use client";

import { useMemo, useState } from "react";
import Image from "next/image";

import {
    Search,
    MapPin,
    CalendarDays,
    Clock,
    Ticket,
    Sparkles,
    MessageCircle,
    ArrowRight,
    X,
    Send,
} from "lucide-react";

import HeroScene from "@/components/3d/HeroScene";
import SeatMap from "@/components/seats/SeatMap";

type ChatMessage = {
    role: "assistant" | "user";
    text: string;
};

const events = [
    {
        id: 1,
        name: "Sunburn Music Festival",
        category: "Music",
        location: "Bengaluru, Karnataka",
        city: "Bengaluru",
        venue: "Venue to be announced",
        date: "November 14, 2026",
        time: "6:00 PM",
        price: 1499,
        image: "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=900",
        description: "Experience an unforgettable night of electronic music.",
    },
    {
        id: 2,
        name: "Tech Innovation Summit",
        category: "Technology",
        location: "Mysuru, Karnataka",
        city: "Mysuru",
        venue: "Venue to be announced",
        date: "November 18, 2026",
        time: "9:30 AM",
        price: 799,
        image: "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=900",
        description: "Explore new technologies and meet industry experts.",
    },
    {
        id: 3,
        name: "Champions Football Cup",
        category: "Sports",
        location: "Bengaluru, Karnataka",
        city: "Bengaluru",
        venue: "Venue to be announced",
        date: "November 21, 2026",
        time: "5:00 PM",
        price: 499,
        image: "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=900",
        description: "Watch an exciting live football tournament.",
    },
    {
        id: 4,
        name: "Stand-up Comedy Night",
        category: "Entertainment",
        location: "Mysuru, Karnataka",
        city: "Mysuru",
        venue: "Venue to be announced",
        date: "November 25, 2026",
        time: "7:00 PM",
        price: 399,
        image: "https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=900",
        description: "Enjoy an evening filled with laughter and entertainment.",
    },
    {
        id: 5,
        name: "Live Classical Concert",
        category: "Music",
        location: "Mangaluru, Karnataka",
        city: "Mangaluru",
        venue: "Venue to be announced",
        date: "November 28, 2026",
        time: "6:30 PM",
        price: 599,
        image: "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=900",
        description: "Enjoy beautiful live music and performances.",
    },
    {
        id: 6,
        name: "Startup Founders Meetup",
        category: "Technology",
        location: "Bengaluru, Karnataka",
        city: "Bengaluru",
        venue: "Venue to be announced",
        date: "December 2, 2026",
        time: "10:00 AM",
        price: 299,
        image: "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=900",
        description: "Connect with founders, developers, and innovators.",
    },
];

const categories = [
    "All",
    "Music",
    "Technology",
    "Sports",
    "Entertainment",
];

export default function Home() {
    const [search, setSearch] = useState("");
    const [category, setCategory] = useState("All");
    const [selectedEvent, setSelectedEvent] = useState<number | null>(null);
    const [chatOpen, setChatOpen] = useState(false);
    const [message, setMessage] = useState("");
    const [isTyping, setIsTyping] = useState(false);

    const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
        {
            role: "assistant",
            text: "Hi! I'm your TicketEase assistant. Ask me about events and tickets.",
        },
    ]);

    const filteredEvents = useMemo(() => {
        return events.filter((event) => {
            const matchesSearch =
                event.name.toLowerCase().includes(search.toLowerCase()) ||
                event.location.toLowerCase().includes(search.toLowerCase());

            const matchesCategory =
                category === "All" || event.category === category;

            return matchesSearch && matchesCategory;
        });
    }, [search, category]);

    const selectedEventDetails = events.find(
        (event) => event.id === selectedEvent
    );

    function getAssistantReply(userText: string) {
        const text = userText.toLowerCase();

        if (
            text.includes("mysuru") ||
            text.includes("mysore") ||
            text.includes("bengaluru") ||
            text.includes("bangalore") ||
            text.includes("mangaluru")
        ) {
            const matchingEvents = events.filter((event) => {
                const location = event.location.toLowerCase();

                return (
                    ((text.includes("mysuru") || text.includes("mysore")) &&
                        location.includes("mysuru")) ||
                    ((text.includes("bengaluru") || text.includes("bangalore")) &&
                        location.includes("bengaluru")) ||
                    (text.includes("mangaluru") &&
                        location.includes("mangaluru"))
                );
            });

            if (matchingEvents.length > 0) {
                return `Here are the events in your selected location:\n\n${matchingEvents
                    .map(
                        (event) =>
                            `• ${event.name}\n  ${event.date} · ${event.time}\n  Ticket price: ₹${event.price}`
                    )
                    .join("\n\n")}\n\nSelect an event on the homepage to explore tickets.`;
            }
        }

        if (
            text.includes("find") ||
            text.includes("event") ||
            text.includes("show") ||
            text.includes("upcoming")
        ) {
            return `Here are our upcoming events:\n\n${events
                .map(
                    (event) =>
                        `• ${event.name}\n  ${event.location}\n  ${event.date} · ${event.time}\n  ₹${event.price}`
                )
                .join("\n\n")}\n\nChoose an event to explore available tickets!`;
        }

        if (text.includes("seat")) {
            return "To check available seats:\n\n1. Explore the upcoming events.\n2. Select your preferred event.\n3. Click Select Tickets.\n4. Choose your seats from the interactive seat map.\n\nThe seat map currently uses demo seat availability.";
        }

        if (
            text.includes("book") ||
            text.includes("ticket") ||
            text.includes("payment") ||
            text.includes("checkout")
        ) {
            return "Here is how to book your tickets:\n\n1. Explore upcoming events.\n2. Select your preferred event.\n3. Choose available seats.\n4. Enter your contact details at checkout.\n\nPayment integration is currently in demo mode. No actual payment is processed.";
        }

        const matchingCategory = categories.find(
            (item) => item !== "All" && text.includes(item.toLowerCase())
        );

        if (matchingCategory) {
            const matchingEvents = events.filter(
                (event) => event.category === matchingCategory
            );

            return `Here are our ${matchingCategory} events:\n\n${matchingEvents
                .map(
                    (event) =>
                        `• ${event.name} — ${event.location} — ₹${event.price}`
                )
                .join("\n")}\n\nSelect an event to explore tickets.`;
        }

        if (text.includes("help") || text.includes("how")) {
            return "I can help you with:\n\n• Finding upcoming events\n• Checking event locations and prices\n• Understanding seat selection\n• Getting booking instructions\n• Learning about checkout\n\nWhat would you like to know?";
        }

        if (
            text.includes("hello") ||
            text.includes("hi") ||
            text.includes("hey")
        ) {
            return "Hello! Welcome to TicketEase. I'm here to help you discover events and understand the ticket booking process. What are you looking for?";
        }

        return "Thanks for your message! I can help you find events, check ticket prices, explore seats, and understand the booking process.\n\nTry asking me about Mysuru events, music events, available seats, or booking help.";
    }

    function sendMessage(customMessage?: string) {
        const userMessage = (customMessage ?? message).trim();

        if (!userMessage || isTyping) return;

        setChatMessages((previous) => [
            ...previous,
            { role: "user", text: userMessage },
        ]);

        setMessage("");
        setIsTyping(true);

        setTimeout(() => {
            const reply = getAssistantReply(userMessage);

            setChatMessages((previous) => [
                ...previous,
                { role: "assistant", text: reply },
            ]);

            setIsTyping(false);
        }, 900);
    }

    return (
        <main className="homepage-animated relative isolate min-h-screen overflow-hidden bg-[#080814] text-slate-100">
            {/* Header */}
            <header className="sticky top-0 z-30 border-b border-white/10 bg-[#0b0b1b]/90 backdrop-blur-xl">
                <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-3 sm:px-5 sm:py-4">
                    <a href="#home" className="flex items-center gap-2">
                        <span className="rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 p-2 text-white shadow-lg shadow-violet-500/30">
                            <Ticket size={23} />
                        </span>
                        <span className="text-lg font-extrabold tracking-tight text-white sm:text-xl">
                            Ticket<span className="text-violet-400">Ease</span>
                        </span>
                    </a>

                    <nav className="hidden items-center gap-8 text-sm font-semibold text-slate-400 md:flex">
                        <a href="#home" className="transition hover:text-violet-400">
                            Home
                        </a>
                        <a href="#events" className="transition hover:text-violet-400">
                            Explore Events
                        </a>
                        <button
                            onClick={() => setChatOpen(true)}
                            className="transition hover:text-violet-400"
                        >
                            AI Assistant
                        </button>
                    </nav>

                    <button
                        onClick={() => setChatOpen(true)}
                        className="flex shrink-0 items-center gap-2 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 px-3 py-2.5 text-sm font-semibold text-white shadow-lg shadow-violet-600/20 transition hover:scale-105 hover:shadow-violet-500/40"
                    >
                        <Sparkles size={17} />
                        Ask AI
                    </button>
                </div>
            </header>

            {/* Hero */}
            <section
                id="home"
                className="relative overflow-hidden bg-gradient-to-br from-[#09091a] via-[#171033] to-[#241044] px-4 py-14 text-white sm:px-5 sm:py-20 md:py-28"
            >
                <div className="pointer-events-none absolute -right-20 -top-20 h-80 w-80 rounded-full bg-violet-500/20 blur-[100px]" />
                <div className="pointer-events-none absolute -bottom-32 left-1/3 h-80 w-80 rounded-full bg-fuchsia-500/15 blur-[100px]" />

                <div className="relative mx-auto grid max-w-7xl items-center gap-6 lg:grid-cols-2 lg:gap-10">
                    <div className="max-w-none">
                        <span className="mb-5 inline-flex items-center gap-2 rounded-full border border-violet-400/30 bg-violet-500/10 px-3 py-2 text-xs text-violet-200 shadow-lg shadow-violet-500/10 sm:mb-6 sm:px-4 sm:text-sm">
                            <Sparkles size={16} className="text-violet-400" />
                            Your smart event booking assistant
                        </span>

                        <h1 className="text-3xl font-extrabold leading-tight sm:text-4xl md:text-6xl">
                            Discover events.
                            <br />
                            <span className="bg-gradient-to-r from-violet-300 via-purple-300 to-fuchsia-300 bg-clip-text text-transparent">
                                Book your experience.
                            </span>
                        </h1>

                        <p className="mt-5 max-w-xl text-sm leading-6 text-slate-300 sm:mt-6 sm:text-base sm:leading-7 md:text-lg">
                            Find exciting events, choose your favourite seats, and book
                            tickets easily with our AI-powered booking assistant.
                        </p>

                        {/* Search */}
                        <div className="mt-7 flex w-full max-w-2xl flex-col gap-2 rounded-2xl border border-violet-400/20 bg-[#17152b]/90 p-2 shadow-2xl shadow-violet-950/40 backdrop-blur-xl sm:mt-9 sm:flex-row sm:gap-3 sm:p-3">
                            <div className="flex flex-1 items-center gap-3 px-3">
                                <Search className="shrink-0 text-violet-400" />
                                <input
                                    value={search}
                                    onChange={(event) => setSearch(event.target.value)}
                                    placeholder="Search events or locations..."
                                    aria-label="Search events or locations"
                                    className="w-full bg-transparent py-3 text-sm text-white outline-none placeholder:text-slate-500"
                                />
                            </div>

                            <button
                                onClick={() =>
                                    document.getElementById("events")?.scrollIntoView({
                                        behavior: "smooth",
                                    })
                                }
                                className="rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-7 py-3 font-semibold text-white shadow-lg shadow-violet-600/25 transition hover:scale-[1.02] hover:shadow-violet-500/40"
                            >
                                Find Events
                            </button>
                        </div>

                        {/* Features */}
                        <div className="mt-6 flex flex-wrap gap-x-5 gap-y-3 text-xs text-slate-300 sm:mt-8 sm:gap-6 sm:text-sm">
                            <span className="flex items-center gap-2">
                                <Ticket size={17} className="text-violet-400" />
                                Easy ticket booking
                            </span>
                            <span className="flex items-center gap-2">
                                <Sparkles size={17} className="text-violet-400" />
                                AI assistance
                            </span>
                            <span className="flex items-center gap-2">
                                <CalendarDays size={17} className="text-violet-400" />
                                Upcoming events
                            </span>
                        </div>
                    </div>

                    {/* 3D Hero Scene */}
                    <div className="w-full min-w-0">
                        <HeroScene />
                    </div>
                </div>
            </section>

            {/* Events */}
            <section
                id="events"
                className="relative mx-auto max-w-7xl px-4 py-12 sm:px-5 sm:py-16"
            >
                <div className="pointer-events-none absolute left-0 top-20 h-72 w-72 rounded-full bg-violet-600/5 blur-[100px]" />

                <div className="relative mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
                    <div>
                        <p className="mb-2 text-sm font-bold uppercase tracking-wider text-violet-400">
                            Discover something exciting
                        </p>
                        <h2 className="text-2xl font-extrabold text-white sm:text-3xl">
                            Upcoming Events
                        </h2>
                        <p className="mt-2 text-slate-400">
                            Find and book tickets for events you love.
                        </p>
                    </div>

                    <p className="text-sm font-medium text-slate-500">
                        {filteredEvents.length} events found
                    </p>
                </div>

                {/* Category filters */}
                <div className="relative mb-8 flex flex-wrap gap-2 pb-2">
                    {categories.map((item) => (
                        <button
                            key={item}
                            onClick={() => setCategory(item)}
                            aria-pressed={category === item}
                            className={`shrink-0 rounded-full border px-4 py-2.5 text-sm font-semibold transition-all duration-300 ${
                                category === item
                                    ? "border-violet-500 bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-lg shadow-violet-600/20"
                                    : "border-white/10 bg-[#151526] text-slate-400 hover:border-violet-500/50 hover:bg-violet-500/10 hover:text-violet-300"
                            }`}
                        >
                            {item}
                        </button>
                    ))}
                </div>

                {/* Selected event */}
                {selectedEventDetails && (
                    <div className="mb-6 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-violet-500/30 bg-violet-500/10 p-4">
                        <p className="text-sm font-medium text-violet-200">
                            Selected event: <strong>{selectedEventDetails.name}</strong>
                        </p>
                        <button
                            onClick={() => setSelectedEvent(null)}
                            className="text-sm font-semibold text-violet-400 underline"
                        >
                            Clear selection
                        </button>
                    </div>
                )}

                {/* Event Cards */}
                {filteredEvents.length > 0 ? (
                    <div className="relative grid min-w-0 grid-cols-1 gap-5 sm:grid-cols-2 sm:gap-6 lg:grid-cols-3 lg:gap-7">
                        {filteredEvents.map((event, index) => (
                            <article
                                key={event.id}
                                style={{ animationDelay: `${index * 120}ms` }}
                                className="event-card-3d group relative overflow-hidden rounded-2xl border border-violet-400/15 bg-[#131326] shadow-xl shadow-black/30 transition-all duration-500 hover:-translate-y-3 hover:border-violet-400/60 hover:shadow-2xl hover:shadow-violet-600/20"
                            >
                                <div className="pointer-events-none absolute inset-0 z-10 rounded-2xl bg-gradient-to-br from-violet-500/0 via-fuchsia-500/0 to-indigo-500/0 opacity-0 transition duration-500 group-hover:from-violet-500/10 group-hover:via-fuchsia-500/5 group-hover:to-indigo-500/10 group-hover:opacity-100" />

                                <div className="relative h-48 overflow-hidden sm:h-52">
                                    <Image
                                        src={event.image}
                                        alt={event.name}
                                        fill
                                        unoptimized
                                        sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                                        className="object-cover transition-all duration-700 ease-out group-hover:scale-110 group-hover:rotate-1"
                                    />

                                    <div className="absolute inset-0 bg-gradient-to-t from-[#090914] via-black/10 to-transparent" />
                                    <div className="absolute inset-0 bg-violet-600/0 transition duration-500 group-hover:bg-violet-600/10" />

                                    <span className="absolute left-4 top-4 rounded-full border border-violet-300/30 bg-[#17152b]/85 px-3 py-1.5 text-xs font-bold text-violet-200 shadow-lg shadow-violet-950/30 backdrop-blur-xl transition duration-500 group-hover:-translate-y-1 group-hover:border-violet-300/70 group-hover:bg-violet-600/80 group-hover:text-white">
                                        <span className="mr-1.5 inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-violet-400" />
                                        {event.category}
                                    </span>

                                    <span className="absolute bottom-4 right-4 rounded-xl border border-white/20 bg-black/50 px-3 py-2 text-sm font-extrabold text-white shadow-xl backdrop-blur-lg transition duration-500 group-hover:scale-110 group-hover:border-violet-300/50">
                                        ₹{event.price.toLocaleString("en-IN")}
                                    </span>
                                </div>

                                <div className="relative z-20 p-5">
                                    <h3 className="text-lg font-bold text-white transition-all duration-300 group-hover:translate-x-1 group-hover:text-violet-300">
                                        {event.name}
                                    </h3>
                                    <p className="mt-2 min-h-10 text-sm leading-5 text-slate-400">
                                        {event.description}
                                    </p>

                                    <div className="mt-4 space-y-3 text-sm text-slate-400">
                                        <p className="flex items-center gap-2 transition-colors group-hover:text-slate-200">
                                            <CalendarDays size={17} className="shrink-0 text-violet-400" />
                                            {event.date}
                                        </p>
                                        <p className="flex items-center gap-2 transition-colors group-hover:text-slate-200">
                                            <Clock size={17} className="shrink-0 text-violet-400" />
                                            {event.time}
                                        </p>
                                        <p className="flex items-center gap-2 transition-colors group-hover:text-slate-200">
                                            <MapPin size={17} className="shrink-0 text-violet-400" />
                                            {event.location}
                                        </p>
                                    </div>

                                    <div className="mt-5 flex items-center justify-between gap-2 border-t border-white/10 pt-4">
                                        <div>
                                            <p className="text-xs text-slate-500">Starting from</p>
                                            <p className="text-xl font-extrabold text-violet-300">
                                                ₹{event.price.toLocaleString("en-IN")}
                                            </p>
                                        </div>

                                        <button
                                            onClick={() => {
                                                setSelectedEvent(event.id);
                                                setTimeout(() => {
                                                    document
                                                        .getElementById("seat-selection")
                                                        ?.scrollIntoView({ behavior: "smooth" });
                                                }, 100);
                                            }}
                                            className="group/btn flex shrink-0 items-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-3 py-2.5 text-sm font-bold text-white shadow-lg shadow-violet-600/20 transition-all duration-300 hover:scale-105 hover:shadow-xl hover:shadow-violet-500/40 active:scale-95 sm:px-4"
                                        >
                                            Select Tickets
                                            <ArrowRight
                                                size={16}
                                                className="transition-transform duration-300 group-hover/btn:translate-x-1"
                                            />
                                        </button>
                                    </div>
                                </div>
                            </article>
                        ))}
                    </div>
                ) : (
                    <div className="rounded-2xl border border-dashed border-white/20 bg-[#131326] py-16 text-center">
                        <Search size={35} className="mx-auto text-slate-500" />
                        <h3 className="mt-4 text-lg font-bold text-white">
                            No events found
                        </h3>
                        <p className="mt-2 text-sm text-slate-400">
                            Try another event name, location, or category.
                        </p>
                        <button
                            onClick={() => {
                                setSearch("");
                                setCategory("All");
                            }}
                            className="mt-5 font-semibold text-violet-400 underline"
                        >
                            Clear filters
                        </button>
                    </div>
                )}

                {/* Seat Selection */}
                {selectedEventDetails && (
                    <div id="seat-selection" className="mt-10 scroll-mt-24">
                        <SeatMap
                            eventName={selectedEventDetails.name}
                            price={selectedEventDetails.price}
                            eventDate={selectedEventDetails.date}
                            eventTime={selectedEventDetails.time}
                            venue={selectedEventDetails.venue}
                            city={selectedEventDetails.city}
                        />
                    </div>
                )}
            </section>

            {/* AI Assistant Banner */}
            <section className="relative overflow-hidden border-y border-violet-500/10 bg-gradient-to-br from-[#100d22] via-[#17102e] to-[#0b0b19] px-4 py-10 sm:px-5 sm:py-14">
                <div className="pointer-events-none absolute -right-20 top-0 h-72 w-72 rounded-full bg-violet-600/15 blur-[100px]" />

                <div className="relative mx-auto flex max-w-7xl flex-col items-start justify-between gap-6 rounded-2xl border border-violet-400/20 bg-[#17152b]/80 p-5 shadow-2xl shadow-black/20 backdrop-blur-xl sm:p-8 md:flex-row md:items-center md:p-10">
                    <div>
                        <p className="font-bold tracking-wider text-violet-400">
                            NEED HELP?
                        </p>
                        <h2 className="mt-2 text-2xl font-extrabold text-white">
                            Let AI help you find your next event.
                        </h2>
                        <p className="mt-2 text-sm text-slate-400">
                            Ask questions about events and ticket booking.
                        </p>
                    </div>

                    <button
                        onClick={() => setChatOpen(true)}
                        className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-6 py-3 font-semibold text-white shadow-lg shadow-violet-600/20 transition hover:scale-105 hover:shadow-violet-500/40"
                    >
                        <Sparkles size={18} />
                        Chat with AI
                    </button>
                </div>
            </section>

            {/* Footer */}
            <footer className="border-t border-white/10 bg-[#070710] px-5 py-8 text-center text-sm text-slate-500">
                <p>
                    © 2026 TicketEase. AI-Powered Online Ticketing and Booking Assistant.
                </p>
            </footer>

            {/* Chatbot */}
            {chatOpen && (
                <div className="chat-window fixed bottom-3 right-3 z-50 flex h-[min(70dvh,560px)] max-h-[calc(100dvh-24px)] w-[calc(100vw-24px)] max-w-[420px] flex-col overflow-hidden rounded-2xl border border-violet-400/30 bg-[#111124] shadow-2xl shadow-violet-950/50 sm:bottom-5 sm:right-5 sm:h-[min(620px,calc(100dvh-40px))] sm:w-[min(420px,calc(100vw-40px))]">
                    {/* Chat Header */}
                    <div className="flex shrink-0 items-center justify-between border-b border-white/10 bg-gradient-to-r from-violet-700 to-indigo-700 p-3 text-white sm:p-4">
                        <div className="flex items-center gap-3">
                            <div className="rounded-xl bg-white/15 p-2">
                                <MessageCircle size={21} />
                            </div>
                            <div>
                                <p className="font-bold">TicketEase Assistant</p>
                                <p className="flex items-center gap-1.5 text-xs text-violet-200">
                                    <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
                                    Online · Demo mode
                                </p>
                            </div>
                        </div>

                        <button
                            onClick={() => setChatOpen(false)}
                            aria-label="Close chat"
                            className="rounded-lg p-2 transition hover:rotate-90 hover:bg-white/20"
                        >
                            <X size={20} />
                        </button>
                    </div>

                    {/* Messages */}
                    <div
                        aria-live="polite"
                        className="min-h-0 flex-1 space-y-4 overflow-y-auto overscroll-contain bg-[#0b0b19] p-3 sm:p-4"
                    >
                        {chatMessages.map((item, index) => (
                            <div
                                key={index}
                                className={`chat-message flex ${
                                    item.role === "user" ? "justify-end" : "justify-start"
                                }`}
                            >
                                <div
                                    className={`max-w-[88%] whitespace-pre-line rounded-2xl border p-3 text-sm leading-6 ${
                                        item.role === "user"
                                            ? "rounded-br-sm border-violet-400/30 bg-gradient-to-br from-violet-600 to-indigo-600 text-white shadow-lg shadow-violet-900/20"
                                            : "rounded-bl-sm border-white/10 bg-[#1a1a31] text-slate-200"
                                    }`}
                                >
                                    {item.text}
                                </div>
                            </div>
                        ))}

                        {/* Typing Indicator */}
                        {isTyping && (
                            <div className="flex justify-start">
                                <div
                                    className="flex items-center gap-1 rounded-2xl rounded-bl-sm border border-white/10 bg-[#1a1a31] px-4 py-3"
                                    aria-label="Assistant is typing"
                                >
                                    <span className="typing-dot" />
                                    <span className="typing-dot" />
                                    <span className="typing-dot" />
                                </div>
                            </div>
                        )}

                        {/* Quick Suggestions */}
                        {chatMessages.length === 1 && !isTyping && (
                            <div className="pt-2">
                                <p className="mb-3 text-xs font-semibold text-slate-500">
                                    QUICK SUGGESTIONS
                                </p>
                                <div className="flex flex-wrap gap-2">
                                    {[
                                        "Find Events",
                                        "Check Seats",
                                        "Booking Help",
                                    ].map((prompt) => (
                                        <button
                                            key={prompt}
                                            type="button"
                                            onClick={() => sendMessage(prompt)}
                                            className="rounded-full border border-violet-400/30 bg-violet-500/10 px-3 py-2 text-xs font-semibold text-violet-300 transition duration-300 hover:-translate-y-1 hover:border-violet-400 hover:bg-violet-500/20"
                                        >
                                            {prompt}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Chat Input */}
                    <form
                        onSubmit={(event) => {
                            event.preventDefault();
                            sendMessage();
                        }}
                        className="flex shrink-0 gap-2 border-t border-white/10 bg-[#111124] p-2 sm:p-3"
                    >
                        <input
                            value={message}
                            onChange={(event) => setMessage(event.target.value)}
                            placeholder="Ask about events..."
                            aria-label="Chat message"
                            disabled={isTyping}
                            className="min-w-0 flex-1 rounded-xl border border-white/10 bg-[#1b1b32] px-3 py-3 text-sm text-white outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 disabled:opacity-50"
                        />
                        <button
                            type="submit"
                            disabled={!message.trim() || isTyping}
                            aria-label="Send message"
                            className="chat-send shrink-0 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 p-3 text-white shadow-lg transition duration-300 hover:scale-105 disabled:cursor-not-allowed disabled:opacity-40"
                        >
                            <Send size={18} />
                        </button>
                    </form>
                </div>
            )}
        </main>
    );
}
