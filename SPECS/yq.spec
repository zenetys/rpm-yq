# Supported targets: el8, el9

%define yq_version 4.45.1
%define golang_version 1.22.8

%define gobuild_vendor() %{lua:
    local gobuild = rpm.expand('%{gobuild}')
    gobuild = gobuild:gsub('go build', 'go build -mod=vendor', 1)
    print(gobuild)
}

%define golang_arch() %{lua:
    local rpm2go_arch = { x86_64 = 'amd64' }
    -- aarch64 = 'arm64', ppc64le = 'ppc64le', s390x = 's390x'
    local arch = rpm.expand('%{_arch}')
    if rpm2go_arch[arch] then print(rpm2go_arch[arch])
    else error('Unsupported architecture: '..arch) end
}

Name: yq
Version: %{yq_version}
Release: 1%{?dist}.zenetys
Summary: Portable command-line YAML processor
License: MIT
URL: https://github.com/mikefarah/yq

Source0: https://github.com/mikefarah/yq/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source100: https://go.dev/dl/go%{golang_version}.linux-%{golang_arch}.tar.gz
Source101: https://go.dev/dl/go%{golang_version}.linux-%{golang_arch}.tar.gz.asc
Source102: https://dl.google.com/dl/linux/linux_signing_key.pub

BuildRequires: gnupg2
%if 0%{?rhel} <= 8
BuildRequires: go-srpm-macros >= 2-17
%else
BuildRequires: go-srpm-macros >= 3.2.0
%endif

%description
yq is a lightweight and portable command-line YAML, JSON and XML processor.
yq uses jq like syntax but works with yaml files as well as json, xml,
properties, csv and tsv. It doesn't yet support everything jq does - but it
does support the most common operations and functions, and more is being added
continuously.

%prep
%{gpgverify} --keyring='%{SOURCE102}' --signature='%{SOURCE101}' --data='%{SOURCE100}'
%setup -c -T

mkdir yq
tar xvzf %{SOURCE0} --strip-components 1 -C yq
tar xvzf %{SOURCE100} go/{bin,go.env,pkg,src}

%build
export PATH=$PATH:$PWD/go/bin
export GOPATH=$PWD/gopath

cd yq
govendor_yq=govendor_yq_$(md5sum go.mod |awk '{print $1}').tar.xz
if [ -f %_sourcedir/$govendor_yq ]; then
    tar xvJf %{_sourcedir}/$govendor_yq
else
    go mod vendor
    tar cJf %{_sourcedir}/$govendor_yq ./vendor/
fi
%gobuild_vendor
cd ..

%install
cd yq
install -D -p -m 0755 -t %{buildroot}%{_bindir}/ ./yq
cd ..

%files
%license yq/LICENSE
%{_bindir}/yq
