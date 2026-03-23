import json
import streamlit.components.v1 as components


def show_zoomable_svg(svg_path: str, preview_height: int = 500):
    with open(svg_path, "r", encoding="utf-8") as f:
        svg_content = f.read()

    svg_js_string = json.dumps(svg_content)

    html = f"""
    <div id="svg-preview-wrapper" style="width:100%;">
        <div
            id="svg-preview"
            style="
                width: 100%;
                border: 1px solid #ddd;
                border-radius: 10px;
                background: white;
                overflow: hidden;
                cursor: zoom-in;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 8px;
                box-sizing: border-box;
            "
            title="Click to enlarge"
        ></div>
    </div>

    <div
        id="svg-modal"
        style="
            display: none;
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.92);
            z-index: 999999;
        "
    >
        <button
            id="svg-close"
            style="
                position: absolute;
                top: 16px;
                right: 20px;
                z-index: 1000001;
                background: rgba(255,255,255,0.15);
                color: white;
                border: 1px solid rgba(255,255,255,0.25);
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 18px;
                cursor: pointer;
            "
        >
            ✕
        </button>

        <div
            id="svg-hint"
            style="
                position: absolute;
                top: 16px;
                left: 20px;
                z-index: 1000001;
                color: white;
                background: rgba(255,255,255,0.12);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                font-family: sans-serif;
            "
        >
            Wheel = zoom | Drag = pan | Double-click = reset | Esc = close
        </div>

        <div
            id="svg-stage"
            style="
                position: absolute;
                inset: 0;
                overflow: hidden;
                cursor: grab;
            "
        >
            <div
                id="svg-panzoom"
                style="
                    position: absolute;
                    left: 50%;
                    top: 50%;
                    transform-origin: center center;
                    will-change: transform;
                    user-select: none;
                    -webkit-user-select: none;
                    cursor: grab;
                "
            ></div>
        </div>
    </div>

    <script>
        const svgMarkup = {svg_js_string};

        const preview = document.getElementById("svg-preview");
        const modal = document.getElementById("svg-modal");
        const closeBtn = document.getElementById("svg-close");
        const stage = document.getElementById("svg-stage");
        const panzoom = document.getElementById("svg-panzoom");

        preview.innerHTML = svgMarkup;
        panzoom.innerHTML = svgMarkup;

        function forceResponsiveSvg(container, maxHeightPx=null) {{
            const svg = container.querySelector("svg");
            if (!svg) return;

            svg.style.display = "block";
            svg.style.width = "100%";
            svg.style.height = "auto";
            svg.style.maxWidth = "100%";

            if (maxHeightPx) {{
                svg.style.maxHeight = maxHeightPx + "px";
            }}
        }}

        forceResponsiveSvg(preview, {preview_height - 40});
        forceResponsiveSvg(panzoom);
        
        let scale = 1;
        let minScale = 0.2;
        let maxScale = 12;
        let translateX = 0;
        let translateY = 0;

        let isDragging = false;
        let startX = 0;
        let startY = 0;

        function applyTransform() {{
            panzoom.style.transform =
                `translate(calc(-50% + ${{translateX}}px), calc(-50% + ${{translateY}}px)) scale(${{scale}})`;
        }}

        function resetView() {{
            scale = 1;
            translateX = 0;
            translateY = 0;
            applyTransform();
        }}

        async function openModal() {{
            modal.style.display = "block";
            document.body.style.overflow = "hidden";

            const modalSvg = panzoom.querySelector("svg");
            if (modalSvg) {{
                modalSvg.style.display = "block";
                modalSvg.style.width = "90vw";
                modalSvg.style.height = "auto";
                modalSvg.style.maxWidth = "90vw";
                modalSvg.style.maxHeight = "90vh";
            }}

            panzoom.style.width = "fit-content";
            panzoom.style.height = "fit-content";

            resetView();

            try {{
                if (!document.fullscreenElement) {{
                    await modal.requestFullscreen();
                }}
            }} catch (err) {{
                console.warn("Fullscreen request failed:", err);
            }}
        }}

        async function closeModal() {{
            modal.style.display = "none";
            document.body.style.overflow = "";

            try {{
                if (document.fullscreenElement) {{
                    await document.exitFullscreen();
                }}
            }} catch (err) {{
                console.warn("Exit fullscreen failed:", err);
            }}
        }}

        preview.addEventListener("click", openModal);
        closeBtn.addEventListener("click", closeModal);

        modal.addEventListener("click", (e) => {{
            if (e.target === modal) {{
                closeModal();
            }}
        }});

        document.addEventListener("keydown", (e) => {{
            if (e.key === "Escape") {{
                closeModal();
            }}
        }});

        document.addEventListener("fullscreenchange", () => {{
            if (!document.fullscreenElement) {{
                modal.style.display = "none";
                document.body.style.overflow = "";
            }}
        }});

        stage.addEventListener("dblclick", () => {{
            resetView();
        }});

        stage.addEventListener("wheel", (e) => {{
            e.preventDefault();

            const rect = stage.getBoundingClientRect();
            const mouseX = e.clientX - rect.left - rect.width / 2;
            const mouseY = e.clientY - rect.top - rect.height / 2;

            const oldScale = scale;
            const zoomFactor = e.deltaY < 0 ? 1.12 : 0.89;
            scale = Math.min(maxScale, Math.max(minScale, scale * zoomFactor));

            const scaleRatio = scale / oldScale;

            translateX = mouseX - (mouseX - translateX) * scaleRatio;
            translateY = mouseY - (mouseY - translateY) * scaleRatio;

            applyTransform();
        }}, {{ passive: false }});

        stage.addEventListener("mousedown", (e) => {{
            isDragging = true;
            startX = e.clientX - translateX;
            startY = e.clientY - translateY;
            stage.style.cursor = "grabbing";
            panzoom.style.cursor = "grabbing";
        }});

        window.addEventListener("mousemove", (e) => {{
            if (!isDragging) return;
            translateX = e.clientX - startX;
            translateY = e.clientY - startY;
            applyTransform();
        }});

        window.addEventListener("mouseup", () => {{
            isDragging = false;
            stage.style.cursor = "grab";
            panzoom.style.cursor = "grab";
        }});

        stage.addEventListener("touchstart", (e) => {{
            if (e.touches.length !== 1) return;
            const t = e.touches[0];
            isDragging = true;
            startX = t.clientX - translateX;
            startY = t.clientY - translateY;
        }}, {{ passive: true }});

        stage.addEventListener("touchmove", (e) => {{
            if (!isDragging || e.touches.length !== 1) return;
            const t = e.touches[0];
            translateX = t.clientX - startX;
            translateY = t.clientY - startY;
            applyTransform();
        }}, {{ passive: true }});

        stage.addEventListener("touchend", () => {{
            isDragging = false;
        }});

        applyTransform();
    </script>
    """

    components.html(html, height=preview_height, scrolling=False)