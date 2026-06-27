        let METADATA = {};

        function openSidebar() {
            document.getElementById('sidebar').classList.add('open');
            document.getElementById('sidebarOverlay').classList.add('active');
        }
        function closeSidebar() {
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('sidebarOverlay').classList.remove('active');
        }
        document.getElementById('hamburgerBtn').addEventListener('click', openSidebar);
        document.getElementById('closeSidebar').addEventListener('click', closeSidebar);
        document.getElementById('sidebarOverlay').addEventListener('click', closeSidebar);

        function renderSidebar(metadata) {
            const nav = document.getElementById('sidebarNav');
            let html = '';
            const sections = { '11': [], '12': [] };

            Object.values(metadata).forEach(item => {
                if(sections[item.class]) sections[item.class].push(item);
            });

            for (const [cls, items] of Object.entries(sections)) {
                html += `<div class="nav-section"><div class="nav-section-title">Class ${cls}</div>`;
                items.forEach(item => {
                    let cleanTitle = item.title.replace(/\s*\(\s*\d+\s*pages?\s*\)/i, '');
                    html += `
                        <div class="nav-item" id="nav-${item.id}" onclick="loadContent('${item.id}')">
                            <span class="nav-icon"><i class="fas fa-feather-alt"></i></span>
                            <span>${cleanTitle}</span>
                        </div>
                    `;
                });
                html += `</div>`;
            }
            nav.innerHTML = html;
        }

       function convertMarkdownToBookFormat(htmlContent) {
    const parserNode = document.createElement('div');
    parserNode.innerHTML = htmlContent;

    const finalLayoutWrapper = document.createElement('div');
    let currentColumnBlock = null;

    const makeNewColumnBlock = () => {
        currentColumnBlock = document.createElement('div');
        currentColumnBlock.className = 'book-columns';
        finalLayoutWrapper.appendChild(currentColumnBlock);
    };

    makeNewColumnBlock();
    const sourceNodes = Array.from(parserNode.childNodes);

    sourceNodes.forEach(node => {
        if (node.nodeType !== Node.ELEMENT_NODE) {
            currentColumnBlock.appendChild(node.cloneNode(true));
            return;
        }

        let rawText = node.innerText.trim();
        rawText = rawText.replace(/\s*\(\s*\d+\s*pages?\s*\)/i, '');
        const tag = node.tagName;

        // Capture major section headings to prevent splitting
        if (tag === 'H1' || tag === 'H2' || tag === 'H3' || 
            rawText.toLowerCase() === 'justification of title' || 
            rawText.toLowerCase() === 'theme' || 
            rawText.toLowerCase() === 'summary' || 
            rawText.toLowerCase() === 'character' ||
            rawText.toLowerCase() === 'characters' ||
            rawText.toLowerCase() === 'important questions' ||
            rawText.toLowerCase() === 'notice' ||
            rawText.toLowerCase() === 'grammar' ||
            rawText.toLowerCase() === 'exercise') {
            
            const blockHeader = document.createElement('div');
            blockHeader.className = 'book-section-heading';
            blockHeader.innerText = rawText;
            
            finalLayoutWrapper.appendChild(blockHeader);
            makeNewColumnBlock(); 
        } 
        // Outer simple box container for advertisements
        else if (tag === 'BLOCKQUOTE') {
            const answerBox = document.createElement('div');
            answerBox.className = 'book-answer-box';
            
            const strongHead = node.querySelector('strong');
            if (strongHead) {
                answerBox.innerHTML = `<span class="box-title-center">${strongHead.innerText}</span><div>${node.innerHTML.replace(strongHead.outerHTML, '')}</div>`;
            } else {
                answerBox.innerHTML = node.innerHTML;
            }
            currentColumnBlock.appendChild(answerBox);
        }
        // Question text alignment handler
        else if (rawText.toUpperCase().startsWith('Q1.') || rawText.toUpperCase().startsWith('Q2.') || rawText.toUpperCase().startsWith('Q.')) {
            const questionDiv = document.createElement('div');
            questionDiv.className = 'book-question';
            questionDiv.innerHTML = node.innerHTML;
            currentColumnBlock.appendChild(questionDiv);
        }
        else {
            currentColumnBlock.appendChild(node.cloneNode(true));
        }
    });

    // 🔥 NEW: Replace [br] with <br> everywhere inside the final HTML
    finalLayoutWrapper.innerHTML = finalLayoutWrapper.innerHTML.replace(/\[br\]/g, '<br>');

    return finalLayoutWrapper.innerHTML;
}

        async function loadContent(id) {
            const item = METADATA[id];
            if (!item) return;

            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            const targetNav = document.getElementById(`nav-${id}`);
            if(targetNav) targetNav.classList.add('active');

            let cleanHeadingTitle = item.title.replace(/\s*\(\s*\d+\s*pages?\s*\)/i, '');
            document.getElementById('breadcrumb').innerHTML = `<span>${cleanHeadingTitle}</span>`;
            const area = document.getElementById('contentArea');
            area.innerHTML = `<div style="text-align:center; padding:40px; font-weight:700;">Formatting Pages...</div>`;
            closeSidebar();

            try {
                const response = await fetch(`chapters/${item.file}`);
                if (!response.ok) throw new Error();
                const mdText = await response.text();
                const standardHtml = marked.parse(mdText);
                
                area.innerHTML = `
                    <div class="page-header"><h2>${cleanHeadingTitle}</h2></div>
                    <div class="page-body">${convertMarkdownToBookFormat(standardHtml)}</div>
                    <a class="back-to-top" onclick="window.scrollTo({top:0, behavior:'smooth'})">Back to top</a>
                `;
            } catch (err) {
                // Static Local Fallback Display Mock Data

                area.innerHTML = `
                    <div class="page-header"><h2>${cleanHeadingTitle}</h2></div>
                    <div class="page-body">${convertMarkdownToBookFormat(fallbackData)}</div>
                    <a class="back-to-top" onclick="window.scrollTo({top:0, behavior:'smooth'})">Back to top</a>
                `;
            }
        }

        async function init() {
            try {
                const response = await fetch('metadata.json');
                METADATA = await response.json();
            } catch (e) {
                METADATA = { "1": { "id": "1", "class": "12", "title": "Advertisements", "file": "advertisements.md" } };
            }
            renderSidebar(METADATA);
            loadContent("1");
        }

        document.getElementById('sidebarSearch').addEventListener('input', function(e) {
            const val = e.target.value.toLowerCase().trim();
            document.querySelectorAll('.nav-item').forEach(el => {
                el.style.display = el.textContent.toLowerCase().includes(val) ? 'flex' : 'none';
            });
        });

        window.addEventListener('load', init);