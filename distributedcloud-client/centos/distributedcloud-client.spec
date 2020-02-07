%global pypi_name distributedcloud-client

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%if 0%{?fedora}
%global with_python3 1
%{!?python3_shortver: %global python3_shortver %(%{__python3} -c 'import sys; print(str(sys.version_info.major) + "." + str(sys.version_info.minor))')}
%endif

Name:          %{pypi_name}
Version:       1.0.0
Release:       1%{?_tis_dist}.%{tis_patch_ver}
Summary:       Client Library for Distributed Cloud Services

License:       ASL 2.0
URL:           unknown
Source0:       %{pypi_name}-%{version}.tar.gz

BuildArch:     noarch

BuildRequires: python3-devel
BuildRequires: python3-setuptools
BuildRequires: python3-pip
BuildRequires: python3-wheel
BuildRequires: python3-jsonschema
BuildRequires: python3-keystonemiddleware
BuildRequires: python3-oslo-concurrency
BuildRequires: python3-oslo-config
BuildRequires: python3-oslo-context
BuildRequires: python3-oslo-db
BuildRequires: python3-oslo-i18n
BuildRequires: python3-oslo-log
BuildRequires: python3-oslo-messaging
BuildRequires: python3-oslo-middleware
BuildRequires: python3-oslo-policy
BuildRequires: python3-oslo-rootwrap
BuildRequires: python3-oslo-serialization
BuildRequires: python3-oslo-service
BuildRequires: python3-oslo-utils
BuildRequires: python3-oslo-versionedobjects
BuildRequires: python3-pbr
BuildRequires: python3-routes
BuildRequires: python3-sphinx
BuildRequires: python3-pyOpenSSL
BuildRequires: systemd
BuildRequires: git
# Required to compile translation files
BuildRequires: python3-babel

%description
Client library for Distributed Cloud built on the Distributed Cloud API. It
provides a command-line tool (dcmanager).

Distributed Cloud provides configuration and management of distributed clouds

# DC Manager
%package dcmanagerclient
Summary: DC Manager Client

%description dcmanagerclient
Distributed Cloud Manager Client

%prep
%autosetup -n %{pypi_name}-%{version} -S git

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
rm -rf {test-,}requirements.txt tools/{pip,test}-requires

%build
export PBR_VERSION=%{version}
%{__python3} setup.py build
%py3_build_wheel

%install
export PBR_VERSION=%{version}
%{__python3} setup.py install --skip-build --root %{buildroot}
mkdir -p $RPM_BUILD_ROOT/wheels
install -m 644 dist/*.whl $RPM_BUILD_ROOT/wheels/

%files dcmanagerclient
%license LICENSE
%{python3_sitelib}/dcmanagerclient*
%{python3_sitelib}/distributedcloud_client-*.egg-info
%exclude %{python3_sitelib}/dcmanagerclient/tests
%{_bindir}/dcmanager*

%package wheels
Summary: %{name} wheels

%description wheels
Contains python wheels for %{name}

%files wheels
/wheels/*
