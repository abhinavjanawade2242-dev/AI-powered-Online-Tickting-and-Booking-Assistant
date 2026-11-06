
"use client";

import { useMemo, useState } from "react";
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
import TicketQuantitySelector from "@/components/tickets/TicketQuantitySelector";
import Checkout from "@/components/checkout/Checkout";

type ChatMessage = {
    role: "assistant" | "user";
    text: string;
};

type Language = "en" | "kn" | "hi";

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

const translations = {
    en: {
        home: "Home",
        explore: "Explore Events",
        assistant: "AI Assistant",
        askAI: "Ask AI",
        heroTag: "Your smart event booking assistant",
        heroTitle: "Discover events.",
        heroSubtitle: "Book your experience.",
        heroDescription:
            "Find exciting events, select your ticket quantity, and book tickets easily with our AI-powered booking assistant.",
        search: "Search events or locations...",
        findEvents: "Find Events",
        easyBooking: "Easy ticket booking",
        aiAssistance: "AI assistance",
        upcoming: "Upcoming events",
        discover: "Discover something exciting",
        upcomingTitle: "Upcoming Events",
        eventDescription: "Find and book tickets for events you love.",
        eventsFound: "events found",
        all: "All",
        music: "Music",
        technology: "Technology",
        sports: "Sports",
        entertainment: "Entertainment",
        selected: "Selected event:",
        bookingType: "Booking type: General Admission",
        clearSelection: "Clear selection",
        startingFrom: "Starting from",
        selectTickets: "Select Tickets",
        noEvents: "No events found",
        noEventsDescription: "Try another event name, location, or category.",
        clearFilters: "Clear filters",
        needHelp: "NEED HELP?",
        aiBannerTitle: "Let AI help you find your next event.",
        aiBannerDescription: "Ask questions about events and ticket booking.",
        chatAI: "Chat with AI",
        footer: "AI-Powered Online Ticketing and Booking Assistant.",
        chatTitle: "TicketEase Assistant",
        online: "Online · Demo mode",
        quickSuggestions: "QUICK SUGGESTIONS",
        findEventsSuggestion: "Find Events",
        checkTickets: "Check Tickets",
        bookingHelp: "Booking Help",
        chatPlaceholder: "Ask about events...",
        chatWelcome: "Hi! I'm your TicketEase assistant. Ask me about events and tickets.",
        closeChat: "Close chat",
        ticketPrice: "Ticket price:",
        generalAdmission: "General Admission",
        locationEvents: "Here are the events in your selected location:",
        upcomingEvents: "Here are our upcoming events:",
        selectEventMessage: "Select an event on the homepage to explore tickets.",
        selectAvailable: "Choose an event to explore available tickets!",
        quantityHelp: "TicketEase currently supports General Admission booking. You can select the number of tickets you need for your preferred event.",
        bookingInstructions:
            "Here is how to book your tickets:\n\n1. Explore upcoming events.\n2. Select your preferred event.\n3. Choose the number of tickets.\n4. Enter your contact details at checkout.\n5. Complete the booking process.\n\nPayment integration is currently being developed.",
        helpText:
            "I can help you with:\n\n• Finding upcoming events\n• Checking event locations and prices\n• Selecting ticket quantities\n• Getting booking instructions\n• Learning about checkout\n\nWhat would you like to know?",
        greeting:
            "Hello! Welcome to TicketEase. I'm here to help you discover events and understand the ticket booking process. What are you looking for?",
        defaultReply:
            "Thanks for your message! I can help you find events, check ticket prices, select ticket quantities, and understand the booking process.\n\nTry asking me about Mysuru events, music events, available tickets, or booking help.",
        categoryEvents: "Here are our",
        categoryEnding: "events:",
    },
    kn: {
        home: "ಮುಖಪುಟ",
        explore: "ಕಾರ್ಯಕ್ರಮಗಳನ್ನು ಅನ್ವೇಷಿಸಿ",
        assistant: "AI ಸಹಾಯಕ",
        askAI: "AI ಕೇಳಿ",
        heroTag: "ನಿಮ್ಮ ಸ್ಮಾರ್ಟ್ ಕಾರ್ಯಕ್ರಮ ಬುಕಿಂಗ್ ಸಹಾಯಕ",
        heroTitle: "ಕಾರ್ಯಕ್ರಮಗಳನ್ನು ಅನ್ವೇಷಿಸಿ.",
        heroSubtitle: "ನಿಮ್ಮ ಅನುಭವವನ್ನು ಬುಕ್ ಮಾಡಿ.",
        heroDescription:
            "ಆಸಕ್ತಿದಾಯಕ ಕಾರ್ಯಕ್ರಮಗಳನ್ನು ಹುಡುಕಿ, ಟಿಕೆಟ್‌ಗಳ ಸಂಖ್ಯೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ ಮತ್ತು AI ಸಹಾಯದಿಂದ ಸುಲಭವಾಗಿ ಟಿಕೆಟ್ ಬುಕ್ ಮಾಡಿ.",
        search: "ಕಾರ್ಯಕ್ರಮಗಳು ಅಥವಾ ಸ್ಥಳಗಳನ್ನು ಹುಡುಕಿ...",
        findEvents: "ಕಾರ್ಯಕ್ರಮಗಳನ್ನು ಹುಡುಕಿ",
        easyBooking: "ಸುಲಭ ಟಿಕೆಟ್ ಬುಕಿಂಗ್",
        aiAssistance: "AI ಸಹಾಯ",
        upcoming: "ಮುಂಬರುವ ಕಾರ್ಯಕ್ರಮಗಳು",
        discover: "ಹೊಸದನ್ನು ಅನ್ವೇಷಿಸಿ",
        upcomingTitle: "ಮುಂಬರುವ ಕಾರ್ಯಕ್ರಮಗಳು",
        eventDescription: "ನಿಮಗೆ ಇಷ್ಟವಾದ ಕಾರ್ಯಕ್ರಮಗಳ ಟಿಕೆಟ್‌ಗಳನ್ನು ಹುಡುಕಿ ಮತ್ತು ಬುಕ್ ಮಾಡಿ.",
        eventsFound: "ಕಾರ್ಯಕ್ರಮಗಳು ಕಂಡುಬಂದಿವೆ",
        all: "ಎಲ್ಲಾ",
        music: "ಸಂಗೀತ",
        technology: "ತಂತ್ರಜ್ಞಾನ",
        sports: "ಕ್ರೀಡೆ",
        entertainment: "ಮನರಂಜನೆ",
        selected: "ಆಯ್ಕೆ ಮಾಡಿದ ಕಾರ್ಯಕ್ರಮ:",
        bookingType: "ಬುಕಿಂಗ್ ಪ್ರಕಾರ: ಸಾಮಾನ್ಯ ಪ್ರವೇಶ",
        clearSelection: "ಆಯ್ಕೆಯನ್ನು ತೆರವುಗೊಳಿಸಿ",
        startingFrom: "ಬೆಲೆ ಪ್ರಾರಂಭ",
        selectTickets: "ಟಿಕೆಟ್ ಆಯ್ಕೆಮಾಡಿ",
        noEvents: "ಯಾವುದೇ ಕಾರ್ಯಕ್ರಮಗಳು ಕಂಡುಬಂದಿಲ್ಲ",
        noEventsDescription: "ಬೇರೆ ಕಾರ್ಯಕ್ರಮದ ಹೆಸರು, ಸ್ಥಳ ಅಥವಾ ವರ್ಗವನ್ನು ಪ್ರಯತ್ನಿಸಿ.",
        clearFilters: "ಫಿಲ್ಟರ್‌ಗಳನ್ನು ತೆರವುಗೊಳಿಸಿ",
        needHelp: "ಸಹಾಯ ಬೇಕೇ?",
        aiBannerTitle: "ನಿಮ್ಮ ಮುಂದಿನ ಕಾರ್ಯಕ್ರಮವನ್ನು ಹುಡುಕಲು AI ಸಹಾಯ ಪಡೆಯಿರಿ.",
        aiBannerDescription: "ಕಾರ್ಯಕ್ರಮಗಳು ಮತ್ತು ಟಿಕೆಟ್ ಬುಕಿಂಗ್ ಬಗ್ಗೆ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಿ.",
        chatAI: "AI ಜೊತೆ ಚಾಟ್ ಮಾಡಿ",
        footer: "AI ಆಧಾರಿತ ಆನ್‌ಲೈನ್ ಟಿಕೆಟ್ ಮತ್ತು ಬುಕಿಂಗ್ ಸಹಾಯಕ.",
        chatTitle: "TicketEase ಸಹಾಯಕ",
        online: "ಆನ್‌ಲೈನ್ · ಡೆಮೊ ಮೋಡ್",
        quickSuggestions: "ತ್ವರಿತ ಸಲಹೆಗಳು",
        findEventsSuggestion: "ಕಾರ್ಯಕ್ರಮಗಳನ್ನು ಹುಡುಕಿ",
        checkTickets: "ಟಿಕೆಟ್ ಪರಿಶೀಲಿಸಿ",
        bookingHelp: "ಬುಕಿಂಗ್ ಸಹಾಯ",
        chatPlaceholder: "ಕಾರ್ಯಕ್ರಮಗಳ ಬಗ್ಗೆ ಕೇಳಿ...",
        chatWelcome: "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ TicketEase ಸಹಾಯಕ. ಕಾರ್ಯಕ್ರಮಗಳು ಮತ್ತು ಟಿಕೆಟ್‌ಗಳ ಬಗ್ಗೆ ಕೇಳಿ.",
        closeChat: "ಚಾಟ್ ಮುಚ್ಚಿ",
        ticketPrice: "ಟಿಕೆಟ್ ಬೆಲೆ:",
        generalAdmission: "ಸಾಮಾನ್ಯ ಪ್ರವೇಶ",
        locationEvents: "ನೀವು ಆಯ್ಕೆ ಮಾಡಿದ ಸ್ಥಳದಲ್ಲಿರುವ ಕಾರ್ಯಕ್ರಮಗಳು:",
        upcomingEvents: "ನಮ್ಮ ಮುಂಬರುವ ಕಾರ್ಯಕ್ರಮಗಳು:",
        selectEventMessage: "ಟಿಕೆಟ್‌ಗಳನ್ನು ನೋಡಲು ಮುಖಪುಟದಲ್ಲಿ ಒಂದು ಕಾರ್ಯಕ್ರಮವನ್ನು ಆಯ್ಕೆಮಾಡಿ.",
        selectAvailable: "ಲಭ್ಯವಿರುವ ಟಿಕೆಟ್‌ಗಳನ್ನು ನೋಡಲು ಕಾರ್ಯಕ್ರಮವನ್ನು ಆಯ್ಕೆಮಾಡಿ!",
        quantityHelp: "TicketEase ಪ್ರಸ್ತುತ ಸಾಮಾನ್ಯ ಪ್ರವೇಶ ಬುಕಿಂಗ್ ಅನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ. ನಿಮಗೆ ಬೇಕಾದ ಟಿಕೆಟ್‌ಗಳ ಸಂಖ್ಯೆಯನ್ನು ಆಯ್ಕೆಮಾಡಬಹುದು.",
        bookingInstructions:
            "ಟಿಕೆಟ್ ಬುಕ್ ಮಾಡುವ ವಿಧಾನ:\n\n1. ಮುಂಬರುವ ಕಾರ್ಯಕ್ರಮಗಳನ್ನು ನೋಡಿ.\n2. ನಿಮಗೆ ಬೇಕಾದ ಕಾರ್ಯಕ್ರಮವನ್ನು ಆಯ್ಕೆಮಾಡಿ.\n3. ಟಿಕೆಟ್‌ಗಳ ಸಂಖ್ಯೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ.\n4. ಚೆಕ್‌ಔಟ್‌ನಲ್ಲಿ ಸಂಪರ್ಕ ವಿವರಗಳನ್ನು ನಮೂದಿಸಿ.\n5. ಬುಕಿಂಗ್ ಪ್ರಕ್ರಿಯೆಯನ್ನು ಪೂರ್ಣಗೊಳಿಸಿ.\n\nಪಾವತಿ ವ್ಯವಸ್ಥೆಯನ್ನು ಅಭಿವೃದ್ಧಿಪಡಿಸಲಾಗುತ್ತಿದೆ.",
        helpText:
            "ನಾನು ನಿಮಗೆ ಈ ವಿಷಯಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಬಹುದು:\n\n• ಮುಂಬರುವ ಕಾರ್ಯಕ್ರಮಗಳನ್ನು ಹುಡುಕುವುದು\n• ಸ್ಥಳ ಮತ್ತು ಬೆಲೆಗಳನ್ನು ಪರಿಶೀಲಿಸುವುದು\n• ಟಿಕೆಟ್‌ಗಳ ಸಂಖ್ಯೆಯನ್ನು ಆಯ್ಕೆಮಾಡುವುದು\n• ಬುಕಿಂಗ್ ಸೂಚನೆಗಳನ್ನು ಪಡೆಯುವುದು\n• ಚೆಕ್‌ಔಟ್ ಬಗ್ಗೆ ತಿಳಿದುಕೊಳ್ಳುವುದು\n\nನಿಮಗೆ ಏನು ತಿಳಿಯಬೇಕು?",
        greeting:
            "ನಮಸ್ಕಾರ! TicketEase ಗೆ ಸ್ವಾಗತ. ಕಾರ್ಯಕ್ರಮಗಳನ್ನು ಹುಡುಕಲು ಮತ್ತು ಟಿಕೆಟ್ ಬುಕಿಂಗ್ ಬಗ್ಗೆ ತಿಳಿಯಲು ನಾನು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ. ನಿಮಗೆ ಏನು ಬೇಕು?",
        defaultReply:
            "ನಿಮ್ಮ ಸಂದೇಶಕ್ಕೆ ಧನ್ಯವಾದಗಳು! ಕಾರ್ಯಕ್ರಮಗಳು, ಟಿಕೆಟ್ ಬೆಲೆಗಳು ಮತ್ತು ಬುಕಿಂಗ್ ಬಗ್ಗೆ ನಾನು ಸಹಾಯ ಮಾಡಬಹುದು.\n\nಮೈಸೂರು ಕಾರ್ಯಕ್ರಮಗಳು ಅಥವಾ ಸಂಗೀತ ಕಾರ್ಯಕ್ರಮಗಳ ಬಗ್ಗೆ ಕೇಳಿ.",
        categoryEvents: "ನಮ್ಮ",
        categoryEnding: "ಕಾರ್ಯಕ್ರಮಗಳು:",
    },
    hi: {
        home: "होम",
        explore: "कार्यक्रम खोजें",
        assistant: "AI सहायक",
        askAI: "AI से पूछें",
        heroTag: "आपका स्मार्ट इवेंट बुकिंग सहायक",
        heroTitle: "कार्यक्रम खोजें।",
        heroSubtitle: "अपना अनुभव बुक करें।",
        heroDescription:
            "रोचक कार्यक्रम खोजें, टिकटों की संख्या चुनें और AI की सहायता से आसानी से टिकट बुक करें।",
        search: "कार्यक्रम या स्थान खोजें...",
        findEvents: "कार्यक्रम खोजें",
        easyBooking: "आसान टिकट बुकिंग",
        aiAssistance: "AI सहायता",
        upcoming: "आगामी कार्यक्रम",
        discover: "कुछ रोमांचक खोजें",
        upcomingTitle: "आगामी कार्यक्रम",
        eventDescription: "अपने पसंदीदा कार्यक्रमों के टिकट खोजें और बुक करें।",
        eventsFound: "कार्यक्रम मिले",
        all: "सभी",
        music: "संगीत",
        technology: "प्रौद्योगिकी",
        sports: "खेल",
        entertainment: "मनोरंजन",
        selected: "चयनित कार्यक्रम:",
        bookingType: "बुकिंग प्रकार: सामान्य प्रवेश",
        clearSelection: "चयन हटाएं",
        startingFrom: "शुरुआती कीमत",
        selectTickets: "टिकट चुनें",
        noEvents: "कोई कार्यक्रम नहीं मिला",
        noEventsDescription: "कोई दूसरा कार्यक्रम, स्थान या श्रेणी खोजें।",
        clearFilters: "फ़िल्टर हटाएं",
        needHelp: "मदद चाहिए?",
        aiBannerTitle: "अपना अगला कार्यक्रम खोजने के लिए AI की मदद लें।",
        aiBannerDescription: "कार्यक्रमों और टिकट बुकिंग के बारे में प्रश्न पूछें।",
        chatAI: "AI से चैट करें",
        footer: "AI-संचालित ऑनलाइन टिकट और बुकिंग सहायक।",
        chatTitle: "TicketEase सहायक",
        online: "ऑनलाइन · डेमो मोड",
        quickSuggestions: "त्वरित सुझाव",
        findEventsSuggestion: "कार्यक्रम खोजें",
        checkTickets: "टिकट देखें",
        bookingHelp: "बुकिंग सहायता",
        chatPlaceholder: "कार्यक्रमों के बारे में पूछें...",
        chatWelcome: "नमस्ते! मैं आपका TicketEase सहायक हूँ। कार्यक्रमों और टिकटों के बारे में पूछें।",
        closeChat: "चैट बंद करें",
        ticketPrice: "टिकट की कीमत:",
        generalAdmission: "सामान्य प्रवेश",
        locationEvents: "आपके चुने हुए स्थान के कार्यक्रम:",
        upcomingEvents: "हमारे आगामी कार्यक्रम:",
        selectEventMessage: "टिकट देखने के लिए होमपेज पर एक कार्यक्रम चुनें।",
        selectAvailable: "उपलब्ध टिकट देखने के लिए एक कार्यक्रम चुनें!",
        quantityHelp: "TicketEase वर्तमान में सामान्य प्रवेश बुकिंग का समर्थन करता है। आप अपनी पसंद के कार्यक्रम के लिए टिकटों की संख्या चुन सकते हैं।",
        bookingInstructions:
            "टिकट बुक करने का तरीका:\n\n1. आगामी कार्यक्रम देखें।\n2. अपना पसंदीदा कार्यक्रम चुनें।\n3. टिकटों की संख्या चुनें।\n4. चेकआउट पर संपर्क विवरण दर्ज करें।\n5. बुकिंग प्रक्रिया पूरी करें।\n\nभुगतान सुविधा अभी विकसित की जा रही है।",
        helpText:
            "मैं इन चीज़ों में आपकी मदद कर सकता हूँ:\n\n• आगामी कार्यक्रम खोजना\n• स्थान और कीमतें देखना\n• टिकटों की संख्या चुनना\n• बुकिंग निर्देश प्राप्त करना\n• चेकआउट के बारे में जानना\n\nआप क्या जानना चाहते हैं?",
        greeting:
            "नमस्ते! TicketEase में आपका स्वागत है। मैं कार्यक्रम खोजने और टिकट बुकिंग समझने में आपकी मदद कर सकता हूँ।",
        defaultReply:
            "आपके संदेश के लिए धन्यवाद! मैं कार्यक्रम, टिकट की कीमत और बुकिंग प्रक्रिया के बारे में मदद कर सकता हूँ।\n\nमैसूर के कार्यक्रमों या संगीत कार्यक्रमों के बारे में पूछें।",
        categoryEvents: "हमारे",
        categoryEnding: "कार्यक्रम:",
    },
};

const eventTranslations = {
    kn: {
        1: {
            name: "ಸನ್‌ಬರ್ನ್ ಸಂಗೀತ ಉತ್ಸವ",
            description: "ಎಲೆಕ್ಟ್ರಾನಿಕ್ ಸಂಗೀತದ ಅದ್ಭುತ ರಾತ್ರಿಯನ್ನು ಅನುಭವಿಸಿ.",
        },
        2: {
            name: "ತಂತ್ರಜ್ಞಾನ ನಾವೀನ್ಯತೆ ಶೃಂಗಸಭೆ",
            description: "ಹೊಸ ತಂತ್ರಜ್ಞಾನಗಳನ್ನು ಅನ್ವೇಷಿಸಿ ಮತ್ತು ಉದ್ಯಮ ತಜ್ಞರನ್ನು ಭೇಟಿ ಮಾಡಿ.",
        },
        3: {
            name: "ಚಾಂಪಿಯನ್ಸ್ ಫುಟ್ಬಾಲ್ ಕಪ್",
            description: "ರೋಮಾಂಚಕಾರಿ ನೇರ ಫುಟ್ಬಾಲ್ ಪಂದ್ಯಾವಳಿಯನ್ನು ವೀಕ್ಷಿಸಿ.",
        },
        4: {
            name: "ಸ್ಟ್ಯಾಂಡ್-ಅಪ್ ಕಾಮಿಡಿ ನೈಟ್",
            description: "ನಗು ಮತ್ತು ಮನರಂಜನೆಯಿಂದ ತುಂಬಿದ ಸಂಜೆಯನ್ನು ಆನಂದಿಸಿ.",
        },
        5: {
            name: "ನೇರ ಶಾಸ್ತ್ರೀಯ ಸಂಗೀತ ಕಾರ್ಯಕ್ರಮ",
            description: "ಸುಂದರವಾದ ನೇರ ಸಂಗೀತ ಮತ್ತು ಪ್ರದರ್ಶನಗಳನ್ನು ಆನಂದಿಸಿ.",
        },
        6: {
            name: "ಸ್ಟಾರ್ಟಪ್ ಸಂಸ್ಥಾಪಕರ ಸಭೆ",
            description: "ಸಂಸ್ಥಾಪಕರು, ಡೆವಲಪರ್‌ಗಳು ಮತ್ತು ನವೋದ್ಯಮಿಗಳನ್ನು ಭೇಟಿ ಮಾಡಿ.",
        },
    },
    hi: {
        1: {
            name: "सनबर्न म्यूजिक फेस्टिवल",
            description: "इलेक्ट्रॉनिक संगीत की एक यादगार रात का अनुभव करें।",
        },
        2: {
            name: "टेक इनोवेशन समिट",
            description: "नई तकनीकों को जानें और उद्योग विशेषज्ञों से मिलें।",
        },
        3: {
            name: "चैंपियंस फुटबॉल कप",
            description: "एक रोमांचक लाइव फुटबॉल टूर्नामेंट देखें।",
        },
        4: {
            name: "स्टैंड-अप कॉमेडी नाइट",
            description: "हँसी और मनोरंजन से भरी शाम का आनंद लें।",
        },
        5: {
            name: "लाइव शास्त्रीय संगीत कार्यक्रम",
            description: "सुंदर लाइव संगीत और प्रस्तुतियों का आनंद लें।",
        },
        6: {
            name: "स्टार्टअप संस्थापक मीटअप",
            description: "संस्थापकों, डेवलपर्स और नए उद्यमियों से मिलें।",
        },
    },
};

export default function Home() {
    const [search, setSearch] = useState("");
    const [category, setCategory] = useState("All");
    const [language, setLanguage] = useState<Language>("en");
    const [selectedEvent, setSelectedEvent] = useState<number | null>(null);
    const [selectedQuantity, setSelectedQuantity] = useState(1);
    const [checkoutOpen, setCheckoutOpen] = useState(false);
    const [chatOpen, setChatOpen] = useState(false);
    const [message, setMessage] = useState("");
    const [isTyping, setIsTyping] = useState(false);

    const t = translations[language];

    const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
        {
            role: "assistant",
            text: translations.en.chatWelcome,
        },
    ]);

    const categoryLabels: Record<string, string> = {
        All: t.all,
        Music: t.music,
        Technology: t.technology,
        Sports: t.sports,
        Entertainment: t.entertainment,
    };

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

    function getEventName(event: (typeof events)[number]) {
        if (language === "en") return event.name;

        const translated =
            eventTranslations[language][
            event.id as keyof (typeof eventTranslations)[typeof language]
            ];

        return translated?.name ?? event.name;
    }

    function getEventDescription(event: (typeof events)[number]) {
        if (language === "en") return event.description;

        const translated =
            eventTranslations[language][
            event.id as keyof (typeof eventTranslations)[typeof language]
            ];

        return translated?.description ?? event.description;
    }

    function selectEvent(eventId: number) {
        setSelectedEvent(eventId);
        setSelectedQuantity(1);
        setCheckoutOpen(false);

        setTimeout(() => {
            document
                .getElementById("ticket-selection")
                ?.scrollIntoView({ behavior: "smooth" });
        }, 100);
    }

    function continueWithQuantity(quantity: number) {
        setSelectedQuantity(quantity);
        setCheckoutOpen(true);

        setTimeout(() => {
            document
                .getElementById("checkout-section")
                ?.scrollIntoView({ behavior: "smooth" });
        }, 100);
    }

    function backToTicketSelection() {
        setCheckoutOpen(false);

        setTimeout(() => {
            document
                .getElementById("ticket-selection")
                ?.scrollIntoView({ behavior: "smooth" });
        }, 100);
    }

    function getAssistantReply(userText: string) {
        const text = userText.toLowerCase();

        if (
            text.includes("mysuru") ||
            text.includes("mysore") ||
            text.includes("ಮೈಸೂರು") ||
            text.includes("मैसूर") ||
            text.includes("bengaluru") ||
            text.includes("bangalore") ||
            text.includes("ಬೆಂಗಳೂರು") ||
            text.includes("बेंगलुरु") ||
            text.includes("mangaluru") ||
            text.includes("ಮಂಗಳೂರು") ||
            text.includes("मंगलुरु")
        ) {
            const matchingEvents = events.filter((event) => {
                const location = event.location.toLowerCase();

                return (
                    ((text.includes("mysuru") ||
                        text.includes("mysore") ||
                        text.includes("ಮೈಸೂರು") ||
                        text.includes("मैसूर")) &&
                        location.includes("mysuru")) ||
                    ((text.includes("bengaluru") ||
                        text.includes("bangalore") ||
                        text.includes("ಬೆಂಗಳೂರು") ||
                        text.includes("बेंगलुरु")) &&
                        location.includes("bengaluru")) ||
                    ((text.includes("mangaluru") ||
                        text.includes("ಮಂಗಳೂರು") ||
                        text.includes("मंगलुरु")) &&
                        location.includes("mangaluru"))
                );
            });

            if (matchingEvents.length > 0) {
                return `${t.locationEvents}\n\n${matchingEvents
                    .map(
                        (event) =>
                            `• ${getEventName(event)}\n  ${event.date} · ${event.time}\n  ${t.ticketPrice} ₹${event.price}\n  ${t.generalAdmission}`
                    )
                    .join("\n\n")}\n\n${t.selectEventMessage}`;
            }
        }

        if (
            text.includes("find") ||
            text.includes("event") ||
            text.includes("show") ||
            text.includes("upcoming") ||
            text.includes("ಕಾರ್ಯಕ್ರಮ") ||
            text.includes("कार्यक्रम")
        ) {
            return `${t.upcomingEvents}\n\n${events
                .map(
                    (event) =>
                        `• ${getEventName(event)}\n  ${event.location}\n  ${event.date} · ${event.time}\n  ₹${event.price}\n  ${t.generalAdmission}`
                )
                .join("\n\n")}\n\n${t.selectAvailable}`;
        }

        if (
            text.includes("seat") ||
            text.includes("quantity") ||
            text.includes("ಟಿಕೆಟ್") ||
            text.includes("टिकट")
        ) {
            return t.quantityHelp;
        }

        if (
            text.includes("book") ||
            text.includes("ticket") ||
            text.includes("payment") ||
            text.includes("checkout") ||
            text.includes("ಬುಕಿಂಗ್") ||
            text.includes("बुकिंग")
        ) {
            return t.bookingInstructions;
        }

        const matchingCategory = categories.find(
            (item) =>
                item !== "All" && text.includes(item.toLowerCase())
        );

        if (matchingCategory) {
            const matchingEvents = events.filter(
                (event) => event.category === matchingCategory
            );

            return `${t.categoryEvents} ${categoryLabels[matchingCategory]} ${t.categoryEnding}\n\n${matchingEvents
                .map(
                    (event) =>
                        `• ${getEventName(event)} — ${event.location} — ₹${event.price}`
                )
                .join("\n")}\n\n${t.selectEventMessage}`;
        }

        if (
            text.includes("help") ||
            text.includes("how") ||
            text.includes("ಸಹಾಯ") ||
            text.includes("मदद")
        ) {
            return t.helpText;
        }

        if (
            text.includes("hello") ||
            text.includes("hi") ||
            text.includes("hey") ||
            text.includes("ನಮಸ್ಕಾರ") ||
            text.includes("नमस्ते")
        ) {
            return t.greeting;
        }

        return t.defaultReply;
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
                            {t.home}
                        </a>
                        <a href="#events" className="transition hover:text-violet-400">
                            {t.explore}
                        </a>
                        <button
                            onClick={() => setChatOpen(true)}
                            className="transition hover:text-violet-400"
                        >
                            {t.assistant}
                        </button>
                    </nav>

                    <div className="flex items-center gap-2">
                        <select
                            value={language}
                            onChange={(e) => {
                                const newLanguage = e.target.value as Language;
                                setLanguage(newLanguage);
                                setChatMessages([
                                    {
                                        role: "assistant",
                                        text: translations[newLanguage].chatWelcome,
                                    },
                                ]);
                            }}
                            aria-label="Select language"
                            className="max-w-[115px] rounded-lg border border-white/20 bg-[#15152d] px-2 py-2.5 text-sm text-white outline-none focus:border-violet-400 sm:max-w-none sm:px-3"
                        >
                            <option value="en">English</option>
                            <option value="kn">ಕನ್ನಡ</option>
                            <option value="hi">हिन्दी</option>
                        </select>

                        <button
                            onClick={() => setChatOpen(true)}
                            className="flex shrink-0 items-center gap-2 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 px-3 py-2.5 text-sm font-semibold text-white shadow-lg shadow-violet-600/20 transition hover:scale-105 hover:shadow-violet-500/40"
                        >
                            <Sparkles size={17} />
                            <span className="hidden sm:inline">{t.askAI}</span>
                        </button>
                    </div>
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
                            {t.heroTag}
                        </span>

                        <h1 className="text-3xl font-extrabold leading-tight sm:text-4xl md:text-6xl">
                            {t.heroTitle}
                            <br />
                            <span className="bg-gradient-to-r from-violet-300 via-purple-300 to-fuchsia-300 bg-clip-text text-transparent">
                                {t.heroSubtitle}
                            </span>
                        </h1>

                        <p className="mt-5 max-w-xl text-sm leading-6 text-slate-300 sm:mt-6 sm:text-base sm:leading-7 md:text-lg">
                            {t.heroDescription}
                        </p>

                        {/* Search */}
                        <div className="mt-7 flex w-full max-w-2xl flex-col gap-2 rounded-2xl border border-violet-400/20 bg-[#17152b]/90 p-2 shadow-2xl shadow-violet-950/40 backdrop-blur-xl sm:mt-9 sm:flex-row sm:gap-3 sm:p-3">
                            <div className="flex flex-1 items-center gap-3 px-3">
                                <Search className="shrink-0 text-violet-400" />
                                <input
                                    value={search}
                                    onChange={(event) => setSearch(event.target.value)}
                                    placeholder={t.search}
                                    aria-label={t.search}
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
                                {t.findEvents}
                            </button>
                        </div>

                        {/* Features */}
                        <div className="mt-6 flex flex-wrap gap-x-5 gap-y-3 text-xs text-slate-300 sm:mt-8 sm:gap-6 sm:text-sm">
                            <span className="flex items-center gap-2">
                                <Ticket size={17} className="text-violet-400" />
                                {t.easyBooking}
                            </span>
                            <span className="flex items-center gap-2">
                                <Sparkles size={17} className="text-violet-400" />
                                {t.aiAssistance}
                            </span>
                            <span className="flex items-center gap-2">
                                <CalendarDays size={17} className="text-violet-400" />
                                {t.upcoming}
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
                            {t.discover}
                        </p>
                        <h2 className="text-2xl font-extrabold text-white sm:text-3xl">
                            {t.upcomingTitle}
                        </h2>
                        <p className="mt-2 text-slate-400">
                            {t.eventDescription}
                        </p>
                    </div>

                    <p className="text-sm font-medium text-slate-500">
                        {filteredEvents.length} {t.eventsFound}
                    </p>
                </div>

                {/* Category filters */}
                <div className="relative mb-8 flex flex-wrap gap-2 pb-2">
                    {categories.map((item) => (
                        <button
                            key={item}
                            onClick={() => setCategory(item)}
                            aria-pressed={category === item}
                            className={`shrink-0 rounded-full border px-4 py-2.5 text-sm font-semibold transition-all duration-300 ${category === item
                                    ? "border-violet-500 bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-lg shadow-violet-600/20"
                                    : "border-white/10 bg-[#151526] text-slate-400 hover:border-violet-500/50 hover:bg-violet-500/10 hover:text-violet-300"
                                }`}
                        >
                            {categoryLabels[item]}
                        </button>
                    ))}
                </div>

                {/* Selected event */}
                {selectedEventDetails && (
                    <div className="mb-6 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-violet-500/30 bg-violet-500/10 p-4">
                        <div>
                            <p className="text-sm font-medium text-violet-200">
                                {t.selected}{" "}
                                <strong>{getEventName(selectedEventDetails)}</strong>
                            </p>
                            <p className="mt-1 text-xs text-violet-300">
                                {t.bookingType}
                            </p>
                        </div>

                        <button
                            onClick={() => {
                                setSelectedEvent(null);
                                setSelectedQuantity(1);
                                setCheckoutOpen(false);
                            }}
                            className="text-sm font-semibold text-violet-400 underline"
                        >
                            {t.clearSelection}
                        </button>
                    </div>
                )}

                {/* Event Cards */}
                {filteredEvents.length > 0 ? (
                    <div className="relative grid min-w-0 grid-cols-1 gap-5 sm:grid-cols-2 sm:gap-6 lg:grid-cols-3 lg:gap-7">
                        {filteredEvents.map((event, index) => (
                            <article
                                key={event.id}
                                style={{
                                    animationDelay: `${index * 120}ms`,
                                }}
                                className="event-card-3d group relative overflow-hidden rounded-2xl border border-violet-400/15 bg-[#131326] shadow-xl shadow-black/30 transition-all duration-500 hover:-translate-y-3 hover:border-violet-400/60 hover:shadow-2xl hover:shadow-violet-600/20"
                            >
                                <div className="pointer-events-none absolute inset-0 z-10 rounded-2xl bg-gradient-to-br from-violet-500/0 via-fuchsia-500/0 to-indigo-500/0 opacity-0 transition duration-500 group-hover:from-violet-500/10 group-hover:via-fuchsia-500/5 group-hover:to-indigo-500/10 group-hover:opacity-100" />

                                <div className="relative h-48 overflow-hidden sm:h-52">
                                    <img
                                        src={event.image}
                                        alt={getEventName(event)}
                                        loading="lazy"
                                        className="h-full w-full object-cover transition-all duration-700 ease-out group-hover:scale-110 group-hover:rotate-1"
                                    />

                                    <div className="absolute inset-0 bg-gradient-to-t from-[#090914] via-black/10 to-transparent" />
                                    <div className="absolute inset-0 bg-violet-600/0 transition duration-500 group-hover:bg-violet-600/10" />

                                    <span className="absolute left-4 top-4 rounded-full border border-violet-300/30 bg-[#17152b]/85 px-3 py-1.5 text-xs font-bold text-violet-200 shadow-lg shadow-violet-950/30 backdrop-blur-xl transition duration-500 group-hover:-translate-y-1 group-hover:border-violet-300/70 group-hover:bg-violet-600/80 group-hover:text-white">
                                        <span className="mr-1.5 inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-violet-400" />
                                        {categoryLabels[event.category]}
                                    </span>

                                    <span className="absolute bottom-4 right-4 rounded-xl border border-white/20 bg-black/50 px-3 py-2 text-sm font-extrabold text-white shadow-xl backdrop-blur-lg transition duration-500 group-hover:scale-110 group-hover:border-violet-300/50">
                                        ₹{event.price.toLocaleString("en-IN")}
                                    </span>
                                </div>

                                <div className="relative z-20 p-5">
                                    <h3 className="text-lg font-bold text-white transition-all duration-300 group-hover:translate-x-1 group-hover:text-violet-300">
                                        {getEventName(event)}
                                    </h3>

                                    <p className="mt-2 min-h-10 text-sm leading-5 text-slate-400">
                                        {getEventDescription(event)}
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
                                            <p className="text-xs text-slate-500">
                                                {t.startingFrom}
                                            </p>
                                            <p className="text-xl font-extrabold text-violet-300">
                                                ₹{event.price.toLocaleString("en-IN")}
                                            </p>
                                        </div>

                                        <button
                                            onClick={() => selectEvent(event.id)}
                                            className="group/btn flex shrink-0 items-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-3 py-2.5 text-sm font-bold text-white shadow-lg shadow-violet-600/20 transition-all duration-300 hover:scale-105 hover:shadow-xl hover:shadow-violet-500/40 active:scale-95 sm:px-4"
                                        >
                                            {t.selectTickets}
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
                            {t.noEvents}
                        </h3>
                        <p className="mt-2 text-sm text-slate-400">
                            {t.noEventsDescription}
                        </p>
                        <button
                            onClick={() => {
                                setSearch("");
                                setCategory("All");
                            }}
                            className="mt-5 font-semibold text-violet-400 underline"
                        >
                            {t.clearFilters}
                        </button>
                    </div>
                )}

                {/* Ticket Selection and Checkout */}
                {selectedEventDetails && (
                    <div id="ticket-selection" className="mt-10 scroll-mt-24">
                        {!checkoutOpen ? (
                            <TicketQuantitySelector
                                eventName={selectedEventDetails.name}
                                price={selectedEventDetails.price}
                                eventDate={selectedEventDetails.date}
                                eventTime={selectedEventDetails.time}
                                venue={selectedEventDetails.venue}
                                city={selectedEventDetails.city}
                                onContinue={continueWithQuantity}
                            />
                        ) : (
                            <div id="checkout-section" className="scroll-mt-24">
                                <Checkout
                                    eventName={selectedEventDetails.name}
                                    price={selectedEventDetails.price}
                                    quantity={selectedQuantity}
                                    eventDate={selectedEventDetails.date}
                                    eventTime={selectedEventDetails.time}
                                    venue={selectedEventDetails.venue}
                                    city={selectedEventDetails.city}
                                    onBack={backToTicketSelection}
                                />
                            </div>
                        )}
                    </div>
                )}
            </section>

            {/* AI Assistant Banner */}
            <section className="relative overflow-hidden border-y border-violet-500/10 bg-gradient-to-br from-[#100d22] via-[#17102e] to-[#0b0b19] px-4 py-10 sm:px-5 sm:py-14">
                <div className="pointer-events-none absolute -right-20 top-0 h-72 w-72 rounded-full bg-violet-600/15 blur-[100px]" />

                <div className="relative mx-auto flex max-w-7xl flex-col items-start justify-between gap-6 rounded-2xl border border-violet-400/20 bg-[#17152b]/80 p-5 shadow-2xl shadow-black/20 backdrop-blur-xl sm:p-8 md:flex-row md:items-center md:p-10">
                    <div>
                        <p className="font-bold tracking-wider text-violet-400">
                            {t.needHelp}
                        </p>
                        <h2 className="mt-2 text-2xl font-extrabold text-white">
                            {t.aiBannerTitle}
                        </h2>
                        <p className="mt-2 text-sm text-slate-400">
                            {t.aiBannerDescription}
                        </p>
                    </div>

                    <button
                        onClick={() => setChatOpen(true)}
                        className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-6 py-3 font-semibold text-white shadow-lg shadow-violet-600/20 transition hover:scale-105 hover:shadow-violet-500/40"
                    >
                        <Sparkles size={18} />
                        {t.chatAI}
                    </button>
                </div>
            </section>

            {/* Footer */}
            <footer className="border-t border-white/10 bg-[#070710] px-5 py-8 text-center text-sm text-slate-500">
                <p>
                    © 2026 TicketEase. {t.footer}
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
                                <p className="font-bold">{t.chatTitle}</p>
                                <p className="flex items-center gap-1.5 text-xs text-violet-200">
                                    <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
                                    {t.online}
                                </p>
                            </div>
                        </div>

                        <button
                            onClick={() => setChatOpen(false)}
                            aria-label={t.closeChat}
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
                                className={`chat-message flex ${item.role === "user"
                                        ? "justify-end"
                                        : "justify-start"
                                    }`}
                            >
                                <div
                                    className={`max-w-[88%] whitespace-pre-line rounded-2xl border p-3 text-sm leading-6 ${item.role === "user"
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
                                    {t.quickSuggestions}
                                </p>
                                <div className="flex flex-wrap gap-2">
                                    {[
                                        t.findEventsSuggestion,
                                        t.checkTickets,
                                        t.bookingHelp,
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
                            placeholder={t.chatPlaceholder}
                            aria-label={t.chatPlaceholder}
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
