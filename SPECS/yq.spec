# Supported targets: el8, el9

%define yq_version 4.50.1

%define gobuild_vendor() %{lua:
    local gobuild = rpm.expand('%{gobuild}')
    gobuild = gobuild:gsub('go build', 'go build -mod=vendor', 1)
    print(gobuild)
}

Name: yq
Version: %{yq_version}
Release: 1%{?dist}.zenetys
Summary: Portable command-line YAML processor
License: MIT
URL: https://github.com/mikefarah/yq

Source0: https://github.com/mikefarah/yq/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

%if 0%{?rhel} <= 8
BuildRequires: go-srpm-macros >= 2-17
%else
BuildRequires: go-srpm-macros >= 3.2.0
%endif

BuildRequires: golang >= 1.24

%description
yq is a lightweight and portable command-line YAML, JSON and XML processor.
yq uses jq like syntax but works with yaml files as well as json, xml,
properties, csv and tsv. It doesn't yet support everything jq does - but it
does support the most common operations and functions, and more is being added
continuously.

%prep
%setup -c -T

mkdir yq
tar xvzf %{SOURCE0} --strip-components 1 -C yq

%build
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
