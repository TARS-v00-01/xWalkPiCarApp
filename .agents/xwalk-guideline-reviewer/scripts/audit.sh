#!/usr/bin/env bash

set -u

SCRIPT_DIRECTORY=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
REPOSITORY_ROOT=$(CDPATH='' cd -- "${SCRIPT_DIRECTORY}/../../.." && pwd)
ISSUE_COUNT=0

report_issue()
{
    local rule_name=$1
    local issue_text=$2

    printf 'ISSUE|%s|%s\n' "${rule_name}" "${issue_text}"
    ISSUE_COUNT=$((ISSUE_COUNT + 1))
}

mapfile -t SOURCE_FILES < <(
    cd "${REPOSITORY_ROOT}" || exit 1
    rg --files \
        -g '*.cpp' \
        -g '*.h' \
        -g '*.hpp' \
        -g '!**/build*/**' \
        -g '!**/CMakeFiles/**' \
        -g '!.agents/**' | sort
)

mapfile -t TEXT_FILES < <(
    cd "${REPOSITORY_ROOT}" || exit 1
    {
        rg --files \
            -g '*.cpp' \
            -g '*.h' \
            -g '*.hpp' \
            -g '*.md' \
            -g 'CMakeLists.txt' \
            -g '!**/build*/**' \
            -g '!**/CMakeFiles/**' \
            -g '!.agents/**'
        printf '%s\n' \
            '.agents/gudlines/CODING_GUIDELINES.md' \
            '.agents/gudlines/DOCUMENTATION_GUIDELINES.md'
    } | sort
)

for relative_file in "${TEXT_FILES[@]}"
do
    while IFS= read -r finding
    do
        report_issue "maximum-line-length" "${finding}"
    done < <(
        awk 'length($0) > 110 {print FILENAME ":" FNR ":" length($0)}' \
            "${REPOSITORY_ROOT}/${relative_file}"
    )

    while IFS= read -r finding
    do
        report_issue "trailing-whitespace" "${relative_file}:${finding}"
    done < <(rg -n '[[:blank:]]+$' "${REPOSITORY_ROOT}/${relative_file}" || true)
done

for relative_file in "${SOURCE_FILES[@]}"
do
    file_name=${relative_file##*/}

    if ! head -n 35 "${REPOSITORY_ROOT}/${relative_file}" | \
        rg -q "@file[[:space:]]+${file_name}"
    then
        report_issue "file-header" "${relative_file}: missing or incorrect @file entry"
    fi

    if ! head -n 35 "${REPOSITORY_ROOT}/${relative_file}" | \
        rg -q '@author[[:space:]]+Joxy John'
    then
        report_issue "file-author" "${relative_file}: author must be Joxy John"
    fi

    if ! head -n 35 "${REPOSITORY_ROOT}/${relative_file}" | \
        rg -q 'Developed using MISRA C\+\+ coding guidelines\.'
    then
        report_issue "misra-note" "${relative_file}: missing required MISRA C++-oriented note"
    fi
done

for relative_file in "${SOURCE_FILES[@]}"
do
    case "${relative_file}" in
        *.h|*.hpp)
            class_count=$(awk '
                /^[[:space:]]*class[[:space:]]+XWalk[A-Za-z0-9_]+/ && $0 !~ /;[[:space:]]*$/ {
                    count += 1
                }
                END {print count + 0}
            ' "${REPOSITORY_ROOT}/${relative_file}")

            if [ "${class_count}" -gt 1 ]
            then
                report_issue "one-class-per-file" \
                    "${relative_file}: contains ${class_count} class definitions"
            fi
            ;;
    esac
done

if [ ! -f "${REPOSITORY_ROOT}/devloper-note/xwalk-rpi5-note/index.md" ]
then
    report_issue "documentation-index" "devloper-note/xwalk-rpi5-note/index.md is missing"
fi

while IFS= read -r unexpected_file
do
    report_issue "documentation-layout" \
        "${unexpected_file}: Markdown must be under devloper-note/xwalk-rpi5-note/Doc/note"
done < <(
    find "${REPOSITORY_ROOT}/devloper-note/xwalk-rpi5-note/Doc" -type f -name '*.md' \
        ! -path '*/devloper-note/xwalk-rpi5-note/Doc/note/*' -print 2>/dev/null
)

while IFS= read -r unexpected_file
do
    report_issue "documentation-layout" \
        "${unexpected_file}: images must be under devloper-note/xwalk-rpi5-note/Doc/image"
done < <(
    find "${REPOSITORY_ROOT}/devloper-note/xwalk-rpi5-note/Doc" -type f \
        \( -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' \) \
        ! -path '*/devloper-note/xwalk-rpi5-note/Doc/image/*' -print 2>/dev/null
)

printf 'SUMMARY|files=%u|issues=%u\n' "${#TEXT_FILES[@]}" "${ISSUE_COUNT}"

if [ "${ISSUE_COUNT}" -ne 0 ]
then
    exit 1
fi

exit 0
