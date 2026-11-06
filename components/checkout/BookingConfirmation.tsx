
"use client";

import { jsPDF } from "jspdf";
import {
    CheckCircle2,
    Download,
    Home,
    Printer,
    Ticket,
} from "lucide-react";

export type BookingDetails = {
    bookingId: string;
    eventName: string;
    eventDate: string;
    eventTime: string;
    venue: string;
    city: string;
    customerName: string;
    email: string;
    phone: string;
    selectedSeats: string[];
    total: number;
};

type BookingConfirmationProps = {
    booking: BookingDetails;
    onBackHome: () => void;
};

export default function BookingConfirmation({
    booking,
    onBackHome,
}: BookingConfirmationProps) {

    const downloadPDF = () => {
        const pdf = new jsPDF({
            orientation: "portrait",
            unit: "mm",
            format: "a5",
        });

        const width = 148;

        pdf.setFillColor(12, 10, 30);
        pdf.rect(0, 0, 148, 210, "F");

        pdf.setFillColor(25, 20, 52);
        pdf.roundedRect(7, 7, 134, 196, 5, 5, "F");

        pdf.setFillColor(91, 33, 182);
        pdf.roundedRect(7, 7, 134, 43, 5, 5, "F");
        pdf.rect(7, 40, 134, 10, "F");

        pdf.setTextColor(255, 255, 255);
        pdf.setFont("helvetica", "bold");
        pdf.setFontSize(23);
        pdf.text("TicketEase", 15, 23);

        pdf.setFont("helvetica", "normal");
        pdf.setFontSize(8);
        pdf.text("YOUR EVENT. YOUR EXPERIENCE.", 15, 30);

        pdf.setFont("helvetica", "bold");
        pdf.setFontSize(9);
        pdf.text("PREMIUM DEMO TICKET", 15, 41);

        pdf.setTextColor(74, 222, 128);
        pdf.setFontSize(12);
        pdf.text("BOOKING CONFIRMED", 15, 59);

        pdf.setTextColor(160, 150, 190);
        pdf.setFontSize(8);
        pdf.text("BOOKING REFERENCE", 15, 67);

        pdf.setTextColor(255, 255, 255);
        pdf.setFontSize(12);
        pdf.text(booking.bookingId, 15, 74);

        pdf.setDrawColor(100, 80, 145);
        pdf.line(15, 80, 133, 80);

        pdf.setTextColor(167, 139, 250);
        pdf.setFontSize(8);
        pdf.text("EVENT NAME", 15, 89);

        pdf.setTextColor(255, 255, 255);
        pdf.setFontSize(14);

        const eventLines = pdf.splitTextToSize(
            booking.eventName,
            112
        );

        pdf.text(eventLines, 15, 97);

        let y = 97 + eventLines.length * 6 + 3;

        // Event details
        pdf.setTextColor(167, 139, 250);
        pdf.setFontSize(8);
        pdf.text("DATE", 15, y);
        pdf.text("TIME", 80, y);

        y += 5;

        pdf.setTextColor(255, 255, 255);
        pdf.setFontSize(8);
        pdf.text(booking.eventDate || "Not specified", 15, y);
        pdf.text(booking.eventTime || "Not specified", 80, y);

        y += 8;

        pdf.setTextColor(167, 139, 250);
        pdf.setFontSize(8);
        pdf.text("VENUE", 15, y);
        pdf.text("CITY", 80, y);

        y += 5;

        pdf.setTextColor(255, 255, 255);
        pdf.setFontSize(8);

        const venueLines = pdf.splitTextToSize(
            booking.venue || "Not specified",
            58
        );

        const cityLines = pdf.splitTextToSize(
            booking.city || "Not specified",
            45
        );

        pdf.text(venueLines, 15, y);
        pdf.text(cityLines, 80, y);

        y += Math.max(venueLines.length, cityLines.length) * 4 + 5;

        pdf.setDrawColor(100, 80, 145);
        pdf.line(15, y, 133, y);

        y += 7;

        // Customer details
        pdf.setTextColor(167, 139, 250);
        pdf.setFontSize(8);
        pdf.text("CUSTOMER DETAILS", 15, y);

        y += 6;

        pdf.setTextColor(235, 235, 245);
        pdf.setFont("helvetica", "normal");
        pdf.setFontSize(8);

        const details = [
            `Name: ${booking.customerName}`,
            `Email: ${booking.email}`,
            `Phone: ${booking.phone}`,
        ];

        details.forEach((detail) => {
            const lines = pdf.splitTextToSize(detail, 112);
            pdf.text(lines, 15, y);
            y += lines.length * 4 + 1;
        });

        // Selected seats
        y += 2;

        pdf.setDrawColor(100, 80, 145);
        pdf.line(15, y, 133, y);

        y += 7;

        pdf.setTextColor(167, 139, 250);
        pdf.setFontSize(8);
        pdf.text("YOUR SEATS", 15, y);

        y += 6;

        pdf.setTextColor(255, 255, 255);
        pdf.setFontSize(9);

        const seats = booking.selectedSeats.join(", ");
        const seatLines = pdf.splitTextToSize(seats, 112);

        pdf.text(seatLines, 15, y);

        y += seatLines.length * 4 + 4;

        // Total amount
        pdf.setFillColor(45, 32, 85);
        pdf.roundedRect(12, y, 124, 15, 3, 3, "F");

        pdf.setTextColor(190, 180, 220);
        pdf.setFontSize(8);
        pdf.text("TOTAL AMOUNT", 18, y + 9);

        pdf.setTextColor(74, 222, 128);
        pdf.setFont("helvetica", "bold");
        pdf.setFontSize(14);

        pdf.text(
            `Rs. ${booking.total.toFixed(2)}`,
            130,
            y + 9,
            { align: "right" }
        );

        // Decorative perforated edge
        pdf.setDrawColor(180, 160, 220);
        pdf.setLineDashPattern([2, 2], 0);
        pdf.line(138, 52, 138, 180);
        pdf.setLineDashPattern([], 0);

        // Decorative barcode
        let barcodeX = 23;
        const barcodeY = 191;

        pdf.setFillColor(255, 255, 255);

        booking.bookingId.split("").forEach((char) => {
            if (barcodeX > 123) return;

            const barWidth = (char.charCodeAt(0) % 3) + 0.5;

            pdf.rect(
                barcodeX,
                barcodeY,
                barWidth,
                4,
                "F"
            );

            barcodeX += barWidth + 1;
        });

        pdf.setTextColor(190, 180, 220);
        pdf.setFont("helvetica", "normal");
        pdf.setFontSize(6);

        pdf.text(
            "TicketEase | AI-Powered Event Booking",
            width / 2,
            199,
            { align: "center" }
        );

        pdf.setTextColor(251, 191, 36);
        pdf.setFontSize(6);

        pdf.text(
            "DEMO ONLY - NOT VALID FOR EVENT ENTRY",
            width / 2,
            202,
            { align: "center" }
        );

        pdf.save(`TicketEase-${booking.bookingId}.pdf`);
    };

    return (
        <div className="min-h-screen bg-[#080814] px-4 py-10 text-white">
            <div className="mx-auto max-w-2xl">

                <div className="rounded-3xl border border-violet-500/30 bg-[#111124] p-6 shadow-2xl shadow-violet-950/30 sm:p-10">

                    <div className="mb-6 text-center">

                        <CheckCircle2
                            size={64}
                            className="mx-auto mb-4 text-green-400"
                        />

                        <span className="rounded-full border border-amber-400/30 bg-amber-400/10 px-4 py-1 text-xs font-bold tracking-wider text-amber-300">
                            DEMO BOOKING
                        </span>

                        <h1 className="mt-5 text-3xl font-bold">
                            Booking Confirmed!
                        </h1>

                        <p className="mt-2 text-slate-400">
                            Your demo ticket is ready.
                        </p>

                    </div>

                    <div className="rounded-2xl border border-violet-400/20 bg-[#19152e] p-5">

                        <div className="mb-5 flex items-center gap-3">

                            <div className="rounded-xl bg-violet-500/20 p-3">
                                <Ticket
                                    className="text-violet-300"
                                    size={28}
                                />
                            </div>

                            <div>
                                <p className="text-xs text-slate-400">
                                    EVENT
                                </p>

                                <h2 className="text-xl font-bold">
                                    {booking.eventName}
                                </h2>
                            </div>

                        </div>

                        <div className="mb-5 rounded-xl border border-dashed border-violet-400/30 p-4">

                            <p className="text-xs text-slate-400">
                                BOOKING REFERENCE
                            </p>

                            <p className="mt-1 break-all text-lg font-bold text-violet-300">
                                {booking.bookingId}
                            </p>

                        </div>

                        {/* Event details */}
                        <div className="mb-5 grid grid-cols-2 gap-4 rounded-xl border border-violet-400/20 bg-violet-500/5 p-4">

                            <div>
                                <p className="text-xs text-slate-400">
                                    DATE
                                </p>
                                <p className="mt-1 font-semibold">
                                    {booking.eventDate}
                                </p>
                            </div>

                            <div>
                                <p className="text-xs text-slate-400">
                                    TIME
                                </p>
                                <p className="mt-1 font-semibold">
                                    {booking.eventTime}
                                </p>
                            </div>

                            <div>
                                <p className="text-xs text-slate-400">
                                    VENUE
                                </p>
                                <p className="mt-1 font-semibold">
                                    {booking.venue}
                                </p>
                            </div>

                            <div>
                                <p className="text-xs text-slate-400">
                                    CITY
                                </p>
                                <p className="mt-1 font-semibold">
                                    {booking.city}
                                </p>
                            </div>

                        </div>

                        {/* Customer details */}
                        <div className="grid gap-4 sm:grid-cols-2">

                            <div>
                                <p className="text-xs text-slate-400">
                                    CUSTOMER
                                </p>
                                <p className="mt-1 font-semibold">
                                    {booking.customerName}
                                </p>
                            </div>

                            <div>
                                <p className="text-xs text-slate-400">
                                    PHONE
                                </p>
                                <p className="mt-1 font-semibold">
                                    {booking.phone}
                                </p>
                            </div>

                            <div className="sm:col-span-2">
                                <p className="text-xs text-slate-400">
                                    EMAIL
                                </p>
                                <p className="mt-1 break-all font-semibold">
                                    {booking.email}
                                </p>
                            </div>

                            <div className="sm:col-span-2">

                                <p className="text-xs text-slate-400">
                                    SELECTED SEATS
                                </p>

                                <div className="mt-2 flex flex-wrap gap-2">

                                    {booking.selectedSeats.map((seat) => (
                                        <span
                                            key={seat}
                                            className="rounded-lg border border-violet-400/30 bg-violet-500/20 px-3 py-2 text-sm font-bold text-violet-200"
                                        >
                                            {seat}
                                        </span>
                                    ))}

                                </div>
                            </div>

                        </div>

                        <div className="mt-6 flex items-center justify-between border-t border-violet-400/20 pt-5">

                            <span className="font-semibold text-slate-300">
                                Total Amount
                            </span>

                            <span className="text-2xl font-bold text-green-400">
                                ₹{booking.total.toFixed(2)}
                            </span>

                        </div>

                    </div>

                    <div className="mt-5 rounded-xl border border-amber-400/20 bg-amber-400/5 p-4 text-sm text-amber-200">

                        <p className="font-semibold">
                            Demo Notice
                        </p>

                        <p className="mt-1 text-amber-200/80">
                            This is a frontend demonstration. No real payment
                            has been processed and no seats have been reserved.
                            The PDF is a demo ticket, not a valid entry pass.
                        </p>

                    </div>

                    <div className="mt-7 grid gap-3 sm:grid-cols-2">

                        <button
                            onClick={downloadPDF}
                            className="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 px-5 py-3 font-bold transition hover:scale-[1.02] hover:shadow-lg hover:shadow-violet-500/30"
                        >
                            <Download size={19} />
                            Download PDF Ticket
                        </button>

                        <button
                            onClick={() => window.print()}
                            className="flex items-center justify-center gap-2 rounded-xl border border-violet-400/30 bg-violet-500/10 px-5 py-3 font-bold transition hover:bg-violet-500/20"
                        >
                            <Printer size={19} />
                            Print Ticket
                        </button>

                        <button
                            onClick={onBackHome}
                            className="flex items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-800/60 px-5 py-3 font-semibold transition hover:bg-slate-700 sm:col-span-2"
                        >
                            <Home size={19} />
                            Back
                        </button>

                    </div>

                </div>
            </div>
        </div>
    );
}
