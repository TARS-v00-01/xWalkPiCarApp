#!/usr/bin/env bash
# Source once per Bash session to update pinned source and Hugging Face assets together.
# Executing the file prepares the checkout but cannot modify the caller's shell.

_xwalk_env_restore()
{
    local root=$1 module
    local -a modules=("$root")
    local inventory
    inventory=$(command git -C "$root" submodule foreach --quiet --recursive 'pwd -P') || return
    while IFS= read -r module; do
        [[ -z "$module" ]] || modules+=("$module")
    done <<< "$inventory"
    for module in "${modules[@]}"; do
        if [[ -f "$module/ci/assets.json" ]]; then
            if [[ ! -f "$module/ci/fetch-assets.sh" ]]; then
                printf 'ERROR Missing asset downloader in %s\n' "$module" >&2
                return 1
            fi
            printf 'xWalk: restoring pinned assets in %s\n' "$module"
            bash "$module/ci/fetch-assets.sh" || return
        fi
    done
}

_xwalk_env_refresh()
{
    local root=$1
    if [[ -f "$root/ci/install-asset-hooks.py" ]]; then
        python3 "$root/ci/install-asset-hooks.py" || return
    fi
    _xwalk_env_restore "$root"
}

_xwalk_env_git()
{
    local argument operation='' root='' top='' parent='' status index=0
    local -a args=("$@") context=()
    # Recognize Git's global options without rewriting the user's command.
    while (( index < ${#args[@]} )); do
        argument=${args[index]}
        case "$argument" in
            -C|-c|--git-dir|--work-tree|--namespace|--config-env)
                (( index + 1 < ${#args[@]} )) || break
                context+=("$argument" "${args[index+1]}")
                index=$((index + 2))
                ;;
            -C?*|-c?*|--git-dir=*|--work-tree=*|--namespace=*|--config-env=*)
                context+=("$argument")
                index=$((index + 1))
                ;;
            --no-pager|--paginate|--no-optional-locks|--no-replace-objects|--literal-pathspecs)
                index=$((index + 1))
                ;;
            pull)
                operation=pull
                break
                ;;
            submodule)
                index=$((index + 1))
                [[ "${args[index]:-}" != --quiet ]] || index=$((index + 1))
                [[ "${args[index]:-}" != -q ]] || index=$((index + 1))
                [[ "${args[index]:-}" != update ]] || operation=update
                break
                ;;
            *) break ;;
        esac
    done
    if [[ -n "$operation" ]]; then
        top=$(command git "${context[@]}" rev-parse --show-toplevel 2>/dev/null) || top=''
        while [[ -n "$top" ]]; do
            if [[ -n "${_XWALK_ENV_ROOTS[$top]:-}" ]]; then
                root=$top
                break
            fi
            parent=$(command git -C "$top" rev-parse --show-superproject-working-tree 2>/dev/null) || parent=''
            [[ "$parent" != "$top" ]] || break
            top=$parent
        done
    fi
    # A dry run must not download or install resources.
    for argument in "${args[@]}"; do
        [[ "$argument" != --dry-run ]] || root=''
    done
    if [[ -z "$root" || "${XWALK_SKIP_ASSETS:-0}" == 1 ]]; then
        command git "$@"
        return $?
    fi
    # Leave user hooks active; only xWalk's asset hook skips duplicate restoration.
    if XWALK_ENV_UPDATING=1 command git "$@"; then
        :
    else
        return $?
    fi
    if _xwalk_env_refresh "$root"; then
        status=0
    else
        status=$?
    fi
    if (( status != 0 )); then
        printf 'ERROR Git succeeded, but xWalk asset restoration failed. Fix access/cache and rerun git submodule update.\n' >&2
    fi
    return "$status"
}

_xwalk_env_main()
{
    local root mode=${1:-setup}
    if (( $# > 1 )); then
        printf 'Usage: source ./xwalk_env.sh [--activate|--help]\n' >&2
        return 2
    fi
    case "$mode" in
        --help|-h)
            printf '%s\n' 'Usage: source ./xwalk_env.sh [--activate|--help]' \
                'Default: initialize pinned submodules, install asset hooks where available, and restore assets.' \
                '--activate: enable the Git wrapper in this Bash session without updating or downloading.' \
                'Then use git pull --ff-only and git submodule update --init --recursive.' \
                'HF_TOKEN or ~/.netrc supplies private Hugging Face access; credentials are never saved here.' \
                'XWALK_SKIP_ASSETS=1 git ... runs a source-only operation.'
            return 0
            ;;
        setup|--activate) ;;
        *) printf 'Unknown option: %s\n' "$mode" >&2; return 2 ;;
    esac
    root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P) || return
    if [[ ! -f "$root/.gitmodules" ]] ||
       [[ "$(command git -C "$root" rev-parse --show-toplevel 2>/dev/null)" != "$root" ]]; then
        printf 'ERROR Source xwalk_env.sh from an integration checkout.\n' >&2
        return 1
    fi
    # Register both integrations when sourced in the same shell; never wrap unrelated repositories.
    declare -gA _XWALK_ENV_ROOTS
    _XWALK_ENV_ROOTS["$root"]=1
    if [[ -n "$(declare -f git)" ]] && [[ "$(declare -f git)" != *'_xwalk_env_git "$@"'* ]]; then
        printf 'ERROR An existing git shell function must be reconciled before enabling xWalk.\n' >&2
        return 1
    fi
    if alias git >/dev/null 2>&1; then
        printf 'ERROR An existing git alias must be reconciled before enabling xWalk.\n' >&2
        return 1
    fi
    function git { _xwalk_env_git "$@"; }
    export XWALK_ASSET_CACHE="${XWALK_ASSET_CACHE:-$HOME/.cache/xwalk-assets}"
    if [[ "$mode" == setup ]]; then
        command -v python3 >/dev/null || { printf 'ERROR Python 3 is required.\n' >&2; return 1; }
        command git -C "$root" submodule sync --recursive || return
        XWALK_ENV_UPDATING=1 command git -C "$root" submodule update --init --recursive || return
        _xwalk_env_refresh "$root" || return
    fi
    printf 'xWalk environment ready: %s\n' "$root"
    if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
        printf 'To enable automatic restoration in your terminal: source "%s/xwalk_env.sh" --activate\n' "$root"
    fi
}

_xwalk_env_main "$@"
