import React, { useRef, useEffect, useState, useCallback } from "react";

/**
 * ScrollCrawlSnake — canvas-based scroll-synced frame sequence animation.
 *
 * Props:
 *   sequenceFolder: e.g. "cobra" → loads /assets/snake-crawl/cobra/frame_001.webp
 *   frameCount: number of frames in the sequence
 *   className: additional CSS class for the wrapper
 *   style: inline styles for the wrapper
 *   alt: accessibility description
 */
export default function ScrollCrawlSnake({
  sequenceFolder,
  frameCount = 100,
  className = "",
  style = {},
  alt = "Snake animation",
}) {
  const wrapperRef = useRef(null);
  const canvasRef = useRef(null);
  const framesRef = useRef([]);
  const loadedRef = useRef(0);
  const [ready, setReady] = useState(false);
  const currentFrameRef = useRef(-1);
  const rafRef = useRef(null);

  /* ── Preload all frames ── */
  useEffect(() => {
    const frames = [];
    let mounted = true;

    for (let i = 1; i <= frameCount; i++) {
      const img = new Image();
      const padded = String(i).padStart(3, "0");
      img.src = `/assets/snake-crawl/${sequenceFolder}/frame_${padded}.webp`;
      img.onload = () => {
        if (!mounted) return;
        loadedRef.current++;
        if (loadedRef.current >= frameCount) {
          setReady(true);
        }
      };
      img.onerror = () => {
        if (!mounted) return;
        loadedRef.current++;
        if (loadedRef.current >= frameCount) setReady(true);
      };
      frames.push(img);
    }

    framesRef.current = frames;
    return () => { mounted = false; };
  }, [sequenceFolder, frameCount]);

  /* ── Draw a specific frame ── */
  const drawFrame = useCallback((index) => {
    const canvas = canvasRef.current;
    const img = framesRef.current[index];
    if (!canvas || !img || !img.complete || !img.naturalWidth) return;

    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    
    // Set canvas internal pixel buffer to high-res based on devicePixelRatio
    if (canvas.width !== img.naturalWidth * dpr || canvas.height !== img.naturalHeight * dpr) {
      canvas.width = img.naturalWidth * dpr;
      canvas.height = img.naturalHeight * dpr;
      ctx.scale(dpr, dpr);
    }
    
    ctx.clearRect(0, 0, img.naturalWidth, img.naturalHeight);
    ctx.drawImage(img, 0, 0, img.naturalWidth, img.naturalHeight);
  }, []);

  /* ── Scroll handler: compute section-local progress ── */
  useEffect(() => {
    if (!ready) return;

    // Draw frame 0 initially
    drawFrame(0);
    currentFrameRef.current = 0;

    const onScroll = () => {
      if (rafRef.current) return; // throttle via rAF
      rafRef.current = requestAnimationFrame(() => {
        rafRef.current = null;
        const wrapper = wrapperRef.current;
        if (!wrapper) return;

        const rect = wrapper.getBoundingClientRect();
        const viewH = window.innerHeight;
        const absTop = rect.top + window.scrollY;

        let progress = 0;
        if (absTop < viewH) {
          // Above the fold (hero): start at 0 when scrollY is 0, finish when scrolled out of view at top
          const totalTravel = absTop + rect.height;
          progress = Math.max(0, Math.min(1, window.scrollY / totalTravel));
        } else {
          // Below the fold: 0 when section top enters viewport bottom, 1 when bottom exits top
          const totalTravel = rect.height + viewH;
          const traveled = viewH - rect.top;
          progress = Math.max(0, Math.min(1, traveled / totalTravel));
        }

        const frameIndex = Math.min(
          frameCount - 1,
          Math.max(0, Math.floor(progress * (frameCount - 1)))
        );

        if (frameIndex !== currentFrameRef.current) {
          currentFrameRef.current = frameIndex;
          drawFrame(frameIndex);
        }
      });
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll(); // initial position

    return () => {
      window.removeEventListener("scroll", onScroll);
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [ready, frameCount, drawFrame]);

  return (
    <div
      ref={wrapperRef}
      className={`scroll-crawl-snake ${className}`}
      style={{ ...style, aspectRatio: "380/676" }}
      role="img"
      aria-label={alt}
    >
      <canvas
        ref={canvasRef}
        className="scroll-crawl-snake__canvas"
        style={{
          width: "100%",
          height: "auto",
          display: "block",
          opacity: ready ? 1 : 0,
          transition: "opacity 0.5s ease",
        }}
      />
    </div>
  );
}
