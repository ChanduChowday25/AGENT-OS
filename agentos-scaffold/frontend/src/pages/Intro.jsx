import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

const VIDEO_SOURCE = "/intro-video.mp4";

export default function Intro() {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const hasCompletedIntroRef = useRef(false);
  const [hasCompletedIntro, setHasCompletedIntro] = useState(false);

  useEffect(() => {
    const video = videoRef.current;

    if (!video) {
      return undefined;
    }

    const handleEnded = () => {
      if (!hasCompletedIntroRef.current) {
        hasCompletedIntroRef.current = true;
        setHasCompletedIntro(true);
      }
      video.currentTime = 0;
      video.play().catch(() => {});
    };

    video.addEventListener("ended", handleEnded);

    video.play().catch(() => {});

    return () => {
      video.removeEventListener("ended", handleEnded);
    };
  }, []);

  const enterWorkspace = () => navigate("/workspace");
  const showEnterWorkspace = hasCompletedIntro;

  return (
    <main className="relative flex h-[100dvh] w-screen items-center justify-center overflow-hidden bg-[#03070b] p-0 text-white">
      <video
        ref={videoRef}
        className="absolute inset-0 h-full w-full object-cover object-center brightness-[1.12] contrast-[1.08]"
        src={VIDEO_SOURCE}
        autoPlay
        muted
        playsInline
        preload="auto"
        aria-hidden="true"
      />
      <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(2,6,10,0.08),rgba(2,6,10,0.18))]" />

      <AnimatePresence>
        {showEnterWorkspace && (
          <motion.button
            type="button"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.7, ease: "easeOut" }}
            onClick={enterWorkspace}
            className="absolute left-[42%] top-[22%] z-10 -translate-x-1/2 -translate-y-1/2 rounded-md border border-cyan-200/55 bg-slate-950/45 px-8 py-4 text-sm font-medium tracking-[0.1em] text-white shadow-[0_0_18px_rgba(103,232,249,0.16)] transition-colors hover:border-cyan-100/85 hover:bg-slate-950/60 focus:outline-none focus:ring-2 focus:ring-cyan-100/60"
          >
            Enter Workspace <span className="text-cyan-100" aria-hidden="true">→</span>
          </motion.button>
        )}
      </AnimatePresence>

      <button
        type="button"
        onClick={enterWorkspace}
        className="absolute bottom-6 right-6 z-10 text-xs tracking-[0.16em] text-white/45 transition-colors hover:text-white/85 focus:outline-none focus:ring-2 focus:ring-cyan-200/60 focus:ring-offset-2 focus:ring-offset-[#03070b]"
      >
        Skip Intro <span aria-hidden="true">→</span>
      </button>
    </main>
  );
}