function convertMarkdownToBookFormat(htmlContent) {
    // 1. Replace custom [C], [B], [U] tags BEFORE parsing
    let preprocessed = htmlContent;

    // [C]…[/C] → centred block (handle multi‑line)
    preprocessed = preprocessed.replace(/\[C\]([\s\S]*?)\[\/C\]/g, '<div class="qa-center">$1</div>');
    // [B]…[/B] → standout bold
    preprocessed = preprocessed.replace(/\[B\]([\s\S]*?)\[\/B\]/g, '<span class="qa-standout-bold">$1</span>');
    // [U]…[/U] → underlined
    preprocessed = preprocessed.replace(/\[U\]([\s\S]*?)\[\/U\]/g, '<span class="qa-underline">$1</span>');

    // 2. Now parse the cleaned HTML
    const parserNode = document.createElement('div');
    parserNode.innerHTML = preprocessed;

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

        // Major section headings – start a new single‑column block
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
        // Manual column split marker
        else if (rawText.toLowerCase() === '[[split]]') {
            const gridWrap = document.createElement('div');
            gridWrap.className = 'col-split-wrap';
            const colLeft = document.createElement('div');
            colLeft.className = 'col-left';
            const colRight = document.createElement('div');
            colRight.className = 'col-right';

            // Move everything accumulated in current block into colLeft
            while (currentColumnBlock.firstChild) {
                colLeft.appendChild(currentColumnBlock.firstChild);
            }

            if (finalLayoutWrapper.lastChild === currentColumnBlock) {
                finalLayoutWrapper.removeChild(currentColumnBlock);
            }

            gridWrap.appendChild(colLeft);
            gridWrap.appendChild(colRight);
            finalLayoutWrapper.appendChild(gridWrap);

            // Everything after [[split]] goes into the right column
            currentColumnBlock = colRight;
        }
        // Boxed answer (blockquote) – now every <strong> becomes a centred title
        else if (tag === 'BLOCKQUOTE') {
            const answerBox = document.createElement('div');
            answerBox.className = 'book-answer-box';

            // Convert ALL <strong> elements to centred, larger titles
            let inner = node.innerHTML;
            inner = inner.replace(/<strong>([\s\S]*?)<\/strong>/g, '<div class="box-title-center">$1</div>');
            answerBox.innerHTML = inner;

            currentColumnBlock.appendChild(answerBox);
        }
        // [Q]…[/Q] – bold & larger
        else if (/^\[Q\]/i.test(rawText) && /\[\/Q\]/i.test(rawText)) {
            const questionDiv = document.createElement('div');
            questionDiv.className = 'qa-q';
            questionDiv.innerHTML = node.innerHTML.replace(/\[Q\]/gi, '').replace(/\[\/Q\]/gi, '');
            currentColumnBlock.appendChild(questionDiv);
        }
        // A: / Ans: – answer
        else if (rawText.toUpperCase().startsWith('A:') || rawText.toUpperCase().startsWith('ANS:')) {
            const answerDiv = document.createElement('div');
            answerDiv.className = 'qa-a';
            answerDiv.innerHTML = node.innerHTML;
            currentColumnBlock.appendChild(answerDiv);
        }
        else {
            currentColumnBlock.appendChild(node.cloneNode(true));
        }
    });

    finalLayoutWrapper.innerHTML = finalLayoutWrapper.innerHTML.replace(/\[br\]/g, '<br>');

    return finalLayoutWrapper.innerHTML;
}