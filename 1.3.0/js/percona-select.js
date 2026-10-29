const selectBox = document.getElementById('versionSelect');

if (selectBox) {
    // Populate the select box with options based on the versionMap
    const versionMap = { 
        'based on Percona Server for MySQL': '/ps/',
        'based on Percona XtraDB Cluster': '/pxc/',
        // Add new versions here as needed
    };

    function getCurrentVersionFromUrl() {
        for (const path of Object.values(versionMap)) {
            if (window.location.pathname.includes(path)) {
                return path;  // Return the matching path as soon as one is found
            }
        }
        return null;  // Return null if no match is found
    }

    Object.keys(versionMap).forEach(version => {
        const option = document.createElement('option');
        option.value = versionMap[version];
        option.textContent = version;
        selectBox.appendChild(option);
    });

    // Set initial selection based on URL
    const currentSegment = getCurrentVersionFromUrl();
    if (currentSegment) {
        selectBox.value = currentSegment;
    }

    // Add event listener for changing URL based on selection
    selectBox.addEventListener('change', function() {
        const selectedVersion = this.value;
        const currentSegment = getCurrentVersionFromUrl();
        if (selectedVersion !== currentSegment) { // Only redirect if the selected version is different
            const newUrl = window.location.href.replace(currentSegment, selectedVersion);
            window.location.href = newUrl;
        }
    });
} else {
    console.log("No version selector available on this website.");
} 

// Product-specific version selector powered by mike's versions.json
const productVersionSelect = document.getElementById('productVersionSelect');

if (productVersionSelect) {
    // Map URL segments to products; extend as needed
    const productMap = {
        '/ps/': 'Percona Server for MySQL',
        '/pxc/': 'Percona XtraDB Cluster'
    };

    function findProductSegment(pathname) {
        const candidates = Object.keys(productMap);
        for (const seg of candidates) {
            const idx = pathname.indexOf(seg);
            if (idx !== -1) return { segment: seg, index: idx };
        }
        return null;
    }

    function getBaseParts() {
        const path = window.location.pathname;
        const hit = findProductSegment(path);
        if (!hit) return null;
        const baseRoot = path.substring(0, hit.index) + hit.segment; // ends with /ps/ or /pxc/
        const after = path.substring(hit.index + hit.segment.length); // e.g., 0.11.0/...
        const parts = after.split('/').filter(p => p.length > 0);
        const currentVersion = parts.length > 0 ? parts[0] : null;
        const remainder = parts.length > 1 ? parts.slice(1).join('/') : '';
        return { baseRoot, currentVersion, remainder };
    }

    function setOptions(versions, selectedVersion) {
        productVersionSelect.innerHTML = '';
        versions.forEach(v => {
            const opt = document.createElement('option');
            opt.value = v.version;
            opt.textContent = v.title || v.version;
            if (v.version === selectedVersion) opt.selected = true;
            productVersionSelect.appendChild(opt);
        });
    }

    const parts = getBaseParts();
    if (parts) {
        // Set a helpful label for screen readers based on the detected product
        const prodLabel = productMap[parts.baseRoot.endsWith('/') ? parts.baseRoot.slice(-4) : parts.baseRoot] || '';
        if (prodLabel) {
            productVersionSelect.setAttribute('aria-label', prodLabel + ' version');
            productVersionSelect.title = prodLabel + ' version';
        }

        fetch(parts.baseRoot + 'versions.json')
            .then(r => (r.ok ? r.json() : []))
            .then(versions => {
                if (!Array.isArray(versions)) return;
                let resolved = null;
                for (const v of versions) {
                    if (v.version === parts.currentVersion || (Array.isArray(v.aliases) && v.aliases.includes(parts.currentVersion))) {
                        resolved = v.version;
                        break;
                    }
                }
                if (!resolved && versions.length > 0) resolved = versions[0].version;
                setOptions(versions, resolved);

                productVersionSelect.addEventListener('change', function() {
                    const newVersion = this.value;
                    const tail = parts.remainder ? '/' + parts.remainder : '';
                    const url = parts.baseRoot + newVersion + tail + window.location.search + window.location.hash;
                    window.location.href = url;
                });
            })
            .catch(() => {
                // Hide selector if we cannot load versions for this product
                const wrapper = productVersionSelect.parentElement;
                if (wrapper) wrapper.style.display = 'none';
            });
    } else {
        // Hide selector when not inside a supported product path
        const wrapper = productVersionSelect.parentElement;
        if (wrapper) wrapper.style.display = 'none';
    }
}