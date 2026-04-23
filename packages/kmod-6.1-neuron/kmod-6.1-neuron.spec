%global kmajor 6.1
%global kernel_sources %{_builddir}/kernel-devel
%global _cross_kmoddir %{_cross_libdir}/modules/%{kmajor}

Name: %{_cross_os}kmod-6.1-neuron
Version: 2.26.10
Release: 1%{?dist}
Epoch: 1
Summary: Modules for the Linux kernel with Neuron hardware
License: MIT AND GPL-2.0-only AND (GPL-2.0-only OR BSD-2-Clause) AND (GPL-2.0 OR Linux-OpenIB) AND (((GPL-2.0 WITH Linux-syscall-note) OR BSD-2-Clause))

# Use latest-neuron-srpm-url.sh to get this.
Source1: https://yum.repos.neuron.amazonaws.com/aws-neuronx-dkms-2.26.10.0.noarch.rpm
Source2: gpgkey-00FA2C1079260870A76D2C285749CAD8646D9185.asc

# Neuron-related configuration and unit files
Source220: neuron-tmpfiles.conf.in
Source221: neuron-latest.toml.in
Source222: load-neuron-latest-modules.service

BuildRequires: %{_cross_os}kernel-6.1-archive
Requires: %{_cross_os}kernel-6.1

Requires: %{_cross_os}ghostdog
Requires: %{_cross_os}variant-platform(aws)
Conflicts: %{_cross_os}variant-flavor(nvidia)
Conflicts: %{_cross_os}variant-flavor(nvidia-fips)

%description
%{summary}.

%prep
tar -xf %{_cross_datadir}/bottlerocket/kernel-devel.tar.xz

rpmkeys --import %{S:2} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:1} --dbpath "${PWD}/rpmdb"
rm -rf "${PWD}/rpmdb"
rpm2cpio %{S:1} | cpio -idmu './usr/src/aws-neuronx-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} neuron_latest \;
rm -r usr

%global kmake %{shrink: \
make -s \
  ARCH="%{_cross_karch}" \
  CROSS_COMPILE="%{_cross_target}-" \
  INSTALL_HDR_PATH="%{buildroot}%{_cross_prefix}" \
  INSTALL_MOD_PATH="%{buildroot}%{_cross_prefix}" \
  INSTALL_MOD_STRIP=1 \
  %{nil}}

%build
%kmake -C %{kernel_sources} %{?_smp_mflags} M=%{_builddir}/neuron_latest

%install
install -d %{buildroot}%{_cross_libexecdir}/neuron/neuron_latest/
%kmake -C %{kernel_sources} %{?_smp_mflags} KERNELRELEASE=%{kmajor} DEPMOD=true INSTALL_MOD_DIR=neuron_latest M=%{_builddir}/neuron_latest modules_install
mv %{buildroot}%{_cross_kmoddir}/neuron_latest/neuron.ko.gz %{buildroot}%{_cross_libexecdir}/neuron/neuron_latest/

# Add Neuron-related configuration files to load the module when the hardware is present.
install -d 0644 %{buildroot}%{_cross_tmpfilesdir}
sed \
  -e "s|__KERNEL_VERSION__|%{kmajor}|" \
  -e "s|__PREFIX__|%{_cross_prefix}|" %{S:220} > neuron.conf
install -p -m 0644 neuron.conf %{buildroot}%{_cross_tmpfilesdir}/
install -d 0644 %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers

sed -e 's|__NEURON_MODULES__|%{_cross_libexecdir}/neuron|' %{S:221} > \
  neuron-latest.toml
install -m 0644 neuron-latest.toml %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers
install -d %{buildroot}%{_cross_unitdir}
install -p -m 0644 %{S:222} %{buildroot}%{_cross_unitdir}

%files
%{_cross_attribution_file}
%{_cross_libexecdir}/neuron/neuron_latest/neuron.ko.gz
%{_cross_tmpfilesdir}/neuron.conf
%{_cross_unitdir}/load-neuron-latest-modules.service
%{_cross_factorydir}%{_cross_sysconfdir}/drivers/neuron-latest.toml

%changelog
