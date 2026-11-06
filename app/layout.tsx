
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "TicketEase | AI-Powered Online Ticket Booking",
  description:
    "Discover events, explore ticket options, and book General Admission tickets easily with TicketEase, your AI-powered ticket booking assistant.",
  applicationName: "TicketEase",
  keywords: [
    "TicketEase",
    "Online Ticket Booking",
    "Event Booking",
    "General Admission",
    "AI Booking Assistant",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        {children}
      </body>
    </html>
  );
}
